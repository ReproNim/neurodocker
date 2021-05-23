"""Container specification renderers."""

from __future__ import annotations

import functools
import inspect
import json
import os
import pathlib
import types
import typing as ty

import jinja2

from neurodocker.reproenv.exceptions import RendererError
from neurodocker.reproenv.exceptions import TemplateError
from neurodocker.reproenv.state import _TemplateRegistry
from neurodocker.reproenv.state import _validate_renderer
from neurodocker.reproenv.template import _BaseInstallationTemplate
from neurodocker.reproenv.template import Template
from neurodocker.reproenv.types import _SingularityHeaderType
from neurodocker.reproenv.types import REPROENV_SPEC_FILE_IN_CONTAINER
from neurodocker.reproenv.types import allowed_pkg_managers
from neurodocker.reproenv.types import allowed_installation_methods
from neurodocker.reproenv.types import installation_methods_type
from neurodocker.reproenv.types import pkg_managers_type

# All jinja2 templates are instantiated from this environment object. It is
# configured to dislike undefined attributes. For example, if a template is
# created with the string '{{ foo.bar }}' and 'foo' does not have a 'bar'
# attribute, an error will be thrown when the jinja template is instantiated.
_jinja_env = jinja2.Environment(undefined=jinja2.StrictUndefined)

# Add globals to the jinja environment. These functions can be called from within a
# template.


def _raise_helper(msg: str) -> ty.NoReturn:
    raise RendererError(msg)


_jinja_env.globals["raise"] = _raise_helper

# TODO: add a flag that avoids buggy behavior when basing a new container on
# one created with ReproEnv.

PathType = ty.Union[str, pathlib.Path, os.PathLike]


def _render_string_from_template(
    source: str, template: _BaseInstallationTemplate
) -> str:
    """Take a string from a template and render """
    # TODO: we could use a while loop or recursive function to render the template until
    # there are no jinja-specific things. At this point, we support one level of
    # nesting.
    n_renders = 0
    max_renders = 20

    err = (
        "A template included in this renderer raised an error. Please check the"
        " template definition. A required argument might not be included in the"
        " required arguments part of the template. Variables in the template should"
        " start with `self.`."
    )

    # Render the string again. This is sometimes necessary because some defaults in the
    # template are rendered as {{ self.X }}. These defaults need to be rendered again.

    while (
        _jinja_env.variable_start_string in source
        and _jinja_env.variable_end_string in source
    ):
        source = source.replace("self.", "template.")
        tmpl = _jinja_env.from_string(source)
        try:
            source = tmpl.render(template=template)
        except jinja2.exceptions.UndefinedError as e:
            raise RendererError(err) from e
        n_renders += 1

        if n_renders > max_renders:
            raise RendererError(
                f"reached maximum rendering iterations ({max_renders}). Templates"
                f" should not nest variables more than {max_renders} times."
            )
    return source


def _log_instruction(func: ty.Callable):
    """Decorator that logs instructions passed to a Renderer.

    This adds the logs to the `_instructions` attribute of the Renderer instance.
    """

    @functools.wraps(func)
    def with_logging(self, *args, **kwds):
        if not hasattr(self, "_instructions"):
            raise ValueError(
                "This wrapper should only be applied to Renderer instances."
            )
        # This gets all arguments, even if their value is None.
        # We remove key-value pairs where value is None, because the schema does not
        # allow for None values.
        # TODO: consider this further...
        sig = inspect.signature(func)

        # We could apply defaults with `bargs.apply_defaults()` but we do not because
        # many defaults are None and the renderer schema does not support null values.
        bargs = sig.bind(self, *args, **kwds)
        # self is not an argument in the spec, but it is present because these are
        # instance methods.
        del bargs.arguments["self"]

        # If a function takes **kwds, save those without wrapping them in another dict.
        # Assume that **kwds arguments are _always_ kwds (eg, not kwargs).
        # TODO: generalize this to work on any VAR_KEYWORD parameter.
        kwds_param = sig.parameters.get("kwds")
        if kwds_param is not None:
            if kwds_param.kind == kwds_param.VAR_KEYWORD:
                bargs_kwds = bargs.arguments.pop("kwds")
                if bargs_kwds is not None:
                    bargs.arguments.update(bargs_kwds)

        d = {"name": func.__name__, "kwds": dict(bargs.arguments)}

        self._instructions["instructions"].append(d)
        return func(self, *args, **kwds)

    return with_logging


class _Renderer:
    def __init__(
        self, pkg_manager: pkg_managers_type, users: ty.Optional[ty.Set[str]] = None
    ) -> None:
        if pkg_manager not in allowed_pkg_managers:
            raise RendererError(
                "Unknown package manager '{}'. Allowed package managers are"
                " '{}'.".format(pkg_manager, "', '".join(allowed_pkg_managers))
            )

        self.pkg_manager = pkg_manager
        self._users = {"root"} if users is None else users
        # This keeps track of the current user. This is useful when saving the JSON
        # specification to JSON, because if we are not root, we can change to root,
        # write the file, and return to whichever user we were.
        self._current_user = "root"
        self._instructions: ty.Mapping = {
            "pkg_manager": self.pkg_manager,
            "existing_users": list(self._users),
            "instructions": [],
        }

        # Strings (comments) that indicate the beginning and end of saving the JSON
        # spec to a file. This helps us in testing because sometimes we don't care
        # about the JSON but we do care about everything else. We can remove the
        # content between these two strings.
        self._json_save_start = "# Save specification to JSON."
        self._json_save_end = "# End saving to specification to JSON."

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, (_Renderer, str)):
            raise NotImplementedError()

        def rm_empty_lines(s):
            return "\n".join(
                j
                for j in str(s).splitlines()
                if j.strip() and not j.strip().startswith("#")
            )

        # Empty lines and commented lines do not affect container definitions.
        return rm_empty_lines(self) == rm_empty_lines(other)

    def __str__(self) -> str:
        masthead = "# Generated by Neurodocker and Reproenv."
        image_spec = self.render()
        return f"{masthead}\n\n{image_spec}"

    @property
    def users(self) -> ty.Set[str]:
        return self._users

    @classmethod
    def from_dict(cls, d: ty.Mapping) -> _Renderer:
        """Instantiate a new renderer from a dictionary of instructions."""
        # raise error if invalid
        _validate_renderer(d)

        pkg_manager = d["pkg_manager"]
        users = d.get("existing_users", None)

        # create new renderer object
        renderer = cls(pkg_manager=pkg_manager, users=users)

        for mapping in d["instructions"]:
            method_or_template = mapping["name"]
            kwds = mapping["kwds"]
            this_instance_method = getattr(renderer, method_or_template, None)
            # Method exists and is something like 'copy', 'env', 'run', etc.
            if this_instance_method is not None:
                try:
                    this_instance_method(**kwds)
                except Exception as e:
                    raise RendererError(
                        f"Error on step '{method_or_template}'. Please see the"
                        " traceback above for details."
                    ) from e
            # This is actually a template.
            else:
                try:
                    renderer.add_registered_template(method_or_template, **kwds)
                except TemplateError as e:
                    raise RendererError(
                        f"Error on template '{method_or_template}'. Please see above"
                        " for more information."
                    ) from e
        return renderer

    def render(self) -> str:
        """Return a rendered string of the container specification.

        This method should take care of combining all of the instructions in a way that
        makes sense for the container type. For a Dockerfile, it might stack the
        sequence of instructions into a string. For a Singularity recipe, it might
        organize the instructions into their respective locations, like %post, %files.

        This method is used by Renderer.__str__ to create the full container spec.
        """
        raise NotImplementedError("subclasses must implement .render()")

    def add_template(
        self, template: Template, method: installation_methods_type
    ) -> _Renderer:
        """Add a template to the renderer.

        Parameters
        ----------
        template : Template
            The template to add. To reference templates by name, use
            `.add_registered_template`.
        method : str
            The method to use to install the software described in the template.
        """

        if not isinstance(template, Template):
            raise RendererError(
                "template must be an instance of 'Template' but got"
                f" '{type(template)}'."
            )
        if method not in allowed_installation_methods:
            raise RendererError(
                "method must be '{}' but got '{}'.".format(
                    "', '".join(sorted(allowed_installation_methods)), method
                )
            )

        template_method: _BaseInstallationTemplate = getattr(template, method)
        if template_method is None:
            raise RendererError(f"template does not have entry for: '{method}'")
        # Validate kwds passed by user to template, and raise an exception if any are
        # invalid.
        template_method.validate_kwds()

        # TODO: print a message if the template has a nonempty `alert` property.
        # If we print to stdout, however, we can cause problems if the user is piping
        # the output to a file or directly to a container build command.

        # If we keep the `self.VAR` syntax of the template, then we need to pass
        # `self=template_method` to the renderer function. But that function is an
        # instance method, so passing `self` will override the `self` argument.
        # To get around this, we replace `self.` with something that is not an
        # argument to the renderer function.

        # Add environment (render any jinja templates).
        if template_method.env:
            d: ty.Mapping[str, str] = {
                _render_string_from_template(
                    k, template_method
                ): _render_string_from_template(v, template_method)
                for k, v in template_method.env.items()
            }
            self.env(**d)

        # Patch the `template_method.install_dependencies` instance method so it can be
        # used (ie rendered) in a template and have access to the pkg_manager requested.
        def install_patch(
            inner_self: _BaseInstallationTemplate, pkgs: ty.List[str], opts: str = None
        ) -> str:
            return _install(pkgs=pkgs, pkg_manager=self.pkg_manager)

        # mypy complains when we try to patch a class, so we do it behind its back with
        # setattr. See https://github.com/python/mypy/issues/2427
        setattr(
            template_method, "install", types.MethodType(install_patch, template_method)
        )

        # Set pkg_manager onto the template.
        setattr(template_method, "pkg_manager", self.pkg_manager)

        # Patch the `template_method.install_dependencies` instance method so it can be
        # used (ie rendered) in a template and have access to the pkg_manager requested.
        def install_dependencies_patch(
            inner_self: _BaseInstallationTemplate, opts: str = None
        ) -> str:
            # TODO: test that template with empty dependencies (apt: []) does not render
            # any installation of dependencies.
            cmd = ""
            pkgs = inner_self.dependencies(pkg_manager=self.pkg_manager)
            if pkgs:
                cmd += _install(pkgs=pkgs, pkg_manager=self.pkg_manager, opts=opts)
            if self.pkg_manager == "apt":
                debs = inner_self.dependencies("debs")
                if debs:
                    cmd += "\n" + _apt_install_debs(debs)
            return cmd

        # mypy complains when we try to patch a class, so we do it behind its back with
        # setattr. See https://github.com/python/mypy/issues/2427
        setattr(
            template_method,
            "install_dependencies",
            types.MethodType(install_dependencies_patch, template_method),
        )

        # Add installation instructions (render any jinja templates).
        if template_method.instructions:
            command = _render_string_from_template(
                template_method.instructions, template_method
            )
            # TODO: raise exception here or skip the run instruction?
            if not command.strip():
                raise RendererError(f"empty rendered instructions in {template.name}")
            self.run(command)

        return self

    def add_registered_template(
        self, name: str, method: installation_methods_type = None, **kwds
    ) -> _Renderer:

        # Template was validated at registration time.
        template_dict = _TemplateRegistry.get(name)

        # By default, prefer 'binaries', but use 'source' if 'binaries' is not defined.
        # TODO: should we require user to provide method?
        if method is None:
            method = "binaries" if "binaries" in template_dict else "source"
        if method not in template_dict:
            raise RendererError(
                f"Installation method '{method}' not defined for template '{name}'."
                " Options are '{}'.".format("', '".join(template_dict.keys()))
            )

        binaries_kwds = source_kwds = None
        if method == "binaries":
            binaries_kwds = kwds
        elif method == "source":
            source_kwds = kwds

        template = Template(
            template=template_dict, binaries_kwds=binaries_kwds, source_kwds=source_kwds
        )

        self.add_template(template=template, method=method)
        return self

    def arg(self, key: str, value: str = None):
        raise NotImplementedError()

    def copy(
        self,
        source: ty.Union[PathType, ty.List[PathType]],
        destination: ty.Union[PathType, ty.List[PathType]],
    ) -> _Renderer:
        raise NotImplementedError()

    def env(self, **kwds: str) -> _Renderer:
        raise NotImplementedError()

    def entrypoint(self, args: ty.List[str]) -> _Renderer:
        raise NotImplementedError()

    def from_(self, base_image: str) -> _Renderer:
        raise NotImplementedError()

    def install(self, pkgs: ty.List[str], opts: str = None) -> _Renderer:
        raise NotImplementedError()

    def label(self, **kwds: str) -> _Renderer:
        raise NotImplementedError()

    def run(self, command: str) -> _Renderer:
        raise NotImplementedError()

    def run_bash(self, command: str) -> _Renderer:
        command = f"bash -c '{command}'"
        return self.run(command)

    def user(self, user: str) -> _Renderer:
        raise NotImplementedError()

    def workdir(self, path: PathType) -> _Renderer:
        raise NotImplementedError()

    def to_json(self, **json_kwds) -> str:
        """Return instructions used in this renderer in JSON format.

        json_kwds are keyword arguments passed to `json.dumps`.
        """
        return json.dumps(self._instructions, **json_kwds)

    def _get_instructions(self) -> str:
        """Return string representation of a printf command that writes the renderer
        instructions to a JSON file in the container.
        """
        j = self.to_json(indent=2)
        # Double-escape escaped sequences so that when printf is done with them, they
        # are escaped with a single slash.
        j = j.replace("\\", "\\\\")
        # Same with parentheses.
        j = j.replace("(", "\\(").replace(")", "\\)")
        # Add slash to the end of each line, except the last.
        j = " \\\n".join(j.splitlines())
        # Escape the % characters so printf does not interpret them as delimiters.
        j = j.replace("%", "%%")
        cmd = f"printf '{j}' > {REPROENV_SPEC_FILE_IN_CONTAINER}"
        return cmd


class DockerRenderer(_Renderer):
    def __init__(
        self, pkg_manager: pkg_managers_type, users: ty.Set[str] = None
    ) -> None:
        super().__init__(pkg_manager=pkg_manager, users=users)
        self._parts: ty.List[str] = []

    def render(self) -> str:
        """Return the rendered Dockerfile."""
        s = "\n".join(self._parts)

        # Save specification to JSON.
        s += f"\n\n{self._json_save_start}"
        if self._current_user != "root":
            s += "\nUSER root"
        s += f"\nRUN {self._get_instructions()}"
        if self._current_user != "root":
            s += f"\nUSER {self._current_user}"
        s += f"\n{self._json_save_end}"
        s = s.strip()  # Prune whitespace from beginning and end.
        return s

    @_log_instruction
    def arg(self, key: str, value: str = None) -> DockerRenderer:
        """Add a Dockerfile `ARG` instruction."""
        s = f"ARG {key}" if value is None else f"ARG {key}={value}"
        self._parts.append(s)
        return self

    @_log_instruction
    def copy(
        self,
        source: ty.Union[PathType, ty.List[PathType]],
        destination: PathType,
        from_: str = None,
        chown: str = None,
    ) -> DockerRenderer:
        """Add a Dockerfile `COPY` instruction."""
        if not isinstance(source, (list, tuple)):
            source = [source]
        source.append(destination)
        files = '["{}"]'.format('", \\\n      "'.join(map(str, source)))
        s = "COPY "
        if from_ is not None:
            s += f"--from={from_} "
        if chown is not None:
            s += f"--chown={chown} "
        s += files
        self._parts.append(s)
        return self

    @_log_instruction
    def env(self, **kwds: str) -> DockerRenderer:
        """Add a Dockerfile `ENV` instruction."""
        s = "ENV " + " \\\n    ".join(f'{k}="{v}"' for k, v in kwds.items())
        self._parts.append(s)
        return self

    @_log_instruction
    def entrypoint(self, args: ty.List[str]) -> DockerRenderer:
        s = 'ENTRYPOINT ["{}"]'.format('", "'.join(args))
        self._parts.append(s)
        return self

    @_log_instruction
    def from_(self, base_image: str, as_: str = None) -> DockerRenderer:
        """Add a Dockerfile `FROM` instruction."""
        if as_ is None:
            s = "FROM " + base_image
        else:
            s = f"FROM {base_image} AS {as_}"
        self._parts.append(s)
        return self

    @_log_instruction
    def install(self, pkgs: ty.List[str], opts=None) -> DockerRenderer:
        """Install system packages."""
        command = _install(pkgs, pkg_manager=self.pkg_manager, opts=opts)
        command = _indent_run_instruction(command)
        self.run(command)
        return self

    @_log_instruction
    def label(self, **kwds: str) -> DockerRenderer:
        """Add a Dockerfile `LABEL` instruction."""
        s = "LABEL " + " \\\n      ".join(f'{k}="{v}"' for k, v in kwds.items())
        self._parts.append(s)
        return self

    @_log_instruction
    def run(self, command: str) -> DockerRenderer:
        """Add a Dockerfile `RUN` instruction."""
        # TODO: should the command be quoted?
        # s = shlex.quote(command)
        # if s.startswith("'"):
        #     s = s[1:-1]  # Remove quotes on either end of the string.
        s = command
        s = _indent_run_instruction(f"RUN {s}")
        self._parts.append(s)
        return self

    @_log_instruction
    def user(self, user: str) -> DockerRenderer:
        """Add a Dockerfile `USER` instruction. If the user is not in
        `self.users`, then a `RUN` instruction that creates the user
        will also be added.
        """
        s = ""
        if user not in self._users:
            s = (
                f'RUN test "$(getent passwd {user})" \\\n    || useradd '
                f"--no-user-group --create-home --shell /bin/bash {user}"
            )
            self._parts.append(s)
            self._users.add(user)
        self._parts.append(f"USER {user}")
        self._current_user = user
        return self

    @_log_instruction
    def workdir(self, path: PathType) -> DockerRenderer:
        """Add a Dockerfile `WORKDIR` instruction."""
        self._parts.append("WORKDIR " + str(path))
        return self


class SingularityRenderer(_Renderer):
    def __init__(
        self, pkg_manager: pkg_managers_type, users: ty.Optional[ty.Set[str]] = None
    ) -> None:
        super().__init__(pkg_manager=pkg_manager, users=users)

        self._header: _SingularityHeaderType = {}
        # The '%setup' section is intentionally ommitted.
        self._files: ty.List[str] = []
        self._environment: ty.List[ty.Tuple[str, str]] = []
        self._post: ty.List[str] = []
        self._runscript = ""
        # TODO: is it OK to use a dict here? Labels could be overwritten.
        self._labels: ty.Dict[str, str] = {}

    def render(self) -> str:
        s = ""
        # Create header.
        if self._header:
            s += (
                f"Bootstrap: {self._header['bootstrap']}\nFrom: {self._header['from_']}"
            )

        # Add files.
        if self._files:
            s += "\n\n%files\n"
            s += "\n".join(self._files)

        # Add environment.
        if self._environment:
            s += "\n\n%environment"
            for k, v in self._environment:
                s += f'\nexport {k}="{v}"'

        # Add post.
        # There will always be a post section, because we always want to add the
        # reproenv specification.
        s += "\n\n%post\n"
        # This section might be empty, but that is OK.
        s += "\n\n".join(self._post)
        s += f"\n\n{self._json_save_start}"
        if self._current_user != "root":
            s += "\nsu - root"
        s += f"\n{self._get_instructions()}"
        if self._current_user != "root":
            s += f"\nsu - {self._current_user}"
        s += f"\n{self._json_save_end}"

        # Add runscript.
        if self._runscript:
            s += "\n\n%runscript\n"
            s += self._runscript

        # Add labels.
        if self._labels:
            s += "\n\n%labels\n"
            for kv in self._labels.items():
                s += " ".join(kv)

        return s

    @_log_instruction
    def arg(self, key: str, value: str = None) -> SingularityRenderer:
        # TODO: look into whether singularity has something like ARG, like passing in
        # environment variables.
        s = f"{key}=" if value is None else f"{key}={value}"
        self._post.append(s)
        return self

    @_log_instruction
    def copy(
        self,
        source: ty.Union[PathType, ty.List[PathType]],
        destination: PathType,
    ) -> SingularityRenderer:
        if not isinstance(source, (list, tuple)):
            source = [source]
        files = [f"{src} {destination}" for src in source]
        self._files.extend(files)
        return self

    @_log_instruction
    def env(self, **kwds: str) -> SingularityRenderer:
        # TODO: why does this raise a type error?
        self._environment.extend(kwds.items())  # type: ignore
        return self

    @_log_instruction
    def entrypoint(self, args: ty.List[str]) -> SingularityRenderer:
        self._runscript = " ".join(args)
        return self

    @_log_instruction
    def from_(self, base_image: str) -> SingularityRenderer:
        if "://" not in base_image:
            bootstrap = "docker"
            image = base_image
        elif base_image.startswith("docker://"):
            bootstrap = "docker"
            image = base_image[9:]
        elif base_image.startswith("library://"):
            bootstrap = "library"
            image = base_image[10:]
        else:
            raise RendererError("Unknown singularity bootstrap agent.")

        self._header = {"bootstrap": bootstrap, "from_": image}
        return self

    @_log_instruction
    def install(self, pkgs: ty.List[str], opts=None) -> SingularityRenderer:
        """Install system packages."""
        command = _install(pkgs, pkg_manager=self.pkg_manager, opts=opts)
        self.run(command)
        return self

    @_log_instruction
    def label(self, **kwds: str) -> SingularityRenderer:
        # TODO: why are we getting this error?
        # Argument 1 to "update" of "dict" has incompatible type
        # "Dict[str, Mapping[str, str]]"; expected "Mapping[str, str]"
        self._labels.update(kwds)  # type: ignore
        return self

    @_log_instruction
    def run(self, command: str) -> SingularityRenderer:
        self._post.append(command)
        return self

    @_log_instruction
    def user(self, user: str) -> SingularityRenderer:
        if user not in self._users:
            post = (
                f'test "$(getent passwd {user})" \\\n|| useradd '
                f"--no-user-group --create-home --shell /bin/bash {user}\n"
            )
            self._users.add(user)
            self._post.append(post)
        self._post.append(f"su - {user}")
        self._current_user = user
        return self

    @_log_instruction
    def workdir(self, path: PathType) -> SingularityRenderer:
        self._post.append(f"mkdir -p {path}\ncd {path}")
        return self


def _indent_run_instruction(string: str, indent=4) -> str:
    """Return indented string for Dockerfile `RUN` command."""
    out = []
    lines = string.splitlines()
    for ii, line in enumerate(lines):
        line = line.rstrip()
        is_last_line = ii == len(lines) - 1
        already_cont = line.startswith(("&&", "&", "||", "|", "fi"))
        is_comment = line.startswith("#")
        previous_cont = lines[ii - 1].endswith("\\") or lines[ii - 1].startswith("if")
        if ii:  # do not apply to first line
            if not already_cont and not previous_cont and not is_comment:
                line = "&& " + line
            if not already_cont and previous_cont:
                line = " " * (indent + 3) + line  # indent + len("&& ")
            else:
                line = " " * indent + line
        if not is_last_line and not line.endswith("\\") and not is_comment:
            line += " \\"
        out.append(line)
    return "\n".join(out)


def _install(pkgs: ty.List[str], pkg_manager: str, opts: str = None) -> str:
    if pkg_manager == "apt":
        return _apt_install(pkgs, opts)
    elif pkg_manager == "yum":
        return _yum_install(pkgs, opts)
    # TODO: add debs here?
    else:
        raise RendererError(f"Unknown package manager '{pkg_manager}'.")


def _apt_install(pkgs: ty.List[str], opts: str = None, sort=True) -> str:
    """Return command to install deb packages with `apt-get` (Debian-based distros).

    `opts` are options passed to `yum install`. Default is "-q --no-install-recommends".
    """
    pkgs = sorted(pkgs) if sort else pkgs
    opts = "-q --no-install-recommends" if opts is None else opts
    s = """\
apt-get update -qq
apt-get install -y {opts} \\
    {pkgs}
rm -rf /var/lib/apt/lists/*
""".format(
        opts=opts, pkgs=" \\\n    ".join(pkgs)
    )
    return s.strip()


def _apt_install_debs(urls: ty.List[str], opts: str = None, sort=True) -> str:
    """Return command to install deb packages with `apt-get` (Debian-based distros).

    `opts` are options passed to `yum install`. Default is "-q".
    """

    def install_one(url: str):
        return f"""\
_reproenv_tmppath="$(mktemp -t tmp.XXXXXXXXXX.deb)"
curl -fsSL --retry 5 -o "${{_reproenv_tmppath}}" {url}
apt-get install --yes {opts} "${{_reproenv_tmppath}}"
rm "${{_reproenv_tmppath}}\""""

    urls = sorted(urls) if sort else urls
    opts = "-q" if opts is None else opts

    s = "\n".join(map(install_one, urls))
    s += """
apt-get update -qq
apt-get install --yes --quiet --fix-missing
rm -rf /var/lib/apt/lists/*"""
    return s


def _yum_install(pkgs: ty.List[str], opts: str = None, sort=True) -> str:
    """Return command to install packages with `yum` (CentOS, Fedora).

    `opts` are options passed to `yum install`. Default is "-q".
    """
    pkgs = sorted(pkgs) if sort else pkgs
    opts = "-q" if opts is None else opts

    s = """\
yum install -y {opts} \\
    {pkgs}
yum clean all
rm -rf /var/cache/yum/*
""".format(
        opts=opts, pkgs=" \\\n    ".join(pkgs)
    )
    return s.strip()
