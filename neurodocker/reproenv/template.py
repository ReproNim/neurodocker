"""Template objects."""

from __future__ import annotations

import copy
import typing as ty

from neurodocker.reproenv.exceptions import TemplateKeywordArgumentError
from neurodocker.reproenv.state import _validate_template
from neurodocker.reproenv.types import _BinariesTemplateType
from neurodocker.reproenv.types import _SourceTemplateType
from neurodocker.reproenv.types import TemplateType


class Template:
    """Template object.

    This class makes it more convenient to work with templates. It also allows one to
    set keyword arguments for instances of templates. For example, if a template calls
    for an argument `version`, this class can be used to hold both the template and the
    value for `version`.

    Keywords are not validated during initialization. To validate keywords, use the
    instance method `self.binaries.validate_kwds()` and`self.source.validate_kwds()`.

    Parameters
    ----------
    template : TemplateType
        Dictionary that defines how to install software from pre-compiled binaries
        and/or from source.
    binaries_kwds : dict
        Keyword arguments to pass to the binaries section of the template. All keys and
        values must be strings.
    source_kwds : dict
        Keyword arguments passed to the source section of the template. All keys and
        values must be strings.
    """

    def __init__(
        self,
        template: TemplateType,
        binaries_kwds: ty.Mapping[str, str] = None,
        source_kwds: ty.Mapping[str, str] = None,
    ):
        # Validate against JSON schema. Registered templates were already validated at
        # registration time, but if we do not validate here, then in-memory templates
        # (ie python dictionaries) will never be validated.
        _validate_template(template)

        self._template = copy.deepcopy(template)
        self._binaries: ty.Optional[_BinariesTemplate] = None
        self._binaries_kwds = {} if binaries_kwds is None else binaries_kwds
        self._source: ty.Optional[_SourceTemplate] = None
        self._source_kwds = {} if source_kwds is None else source_kwds

        if "binaries" in self._template:
            self._binaries = _BinariesTemplate(
                self._template["binaries"], **self._binaries_kwds
            )
        if "source" in self._template:
            self._source = _SourceTemplate(
                self._template["source"], **self._source_kwds
            )

    @property
    def name(self) -> str:
        return self._template["name"]

    @property
    def binaries(self) -> ty.Union[None, _BinariesTemplate]:
        return self._binaries

    @property
    def source(self) -> ty.Union[None, _SourceTemplate]:
        return self._source

    @property
    def alert(self) -> str:
        """Return the template's `alert` property. Return an empty string if it does
        not exist.
        """
        return self._template.get("alert", "")


class _BaseInstallationTemplate:
    """Base class for installation template classes.

    This class and its subclasses make it more convenient to work with templates.
    It also allows one to set keyword arguments for instances of templates. For example,
    if a template calls for an argument `version`, this class can be used to hold both
    the template and the value for `version`.

    Parameters
    ----------
    template : BinariesTemplateType or SourceTemplateType
        Dictionary that defines how to install software from pre-compiled binaries or
        from source.
    kwds
        Keyword arguments to pass to the template. All values must be strings. Values
        that are not strings are cast to string.
    """

    def __init__(
        self,
        template: ty.Union[_BinariesTemplateType, _SourceTemplateType],
        **kwds: str,
    ) -> None:
        self._template = copy.deepcopy(template)
        # User-defined arguments that are passed to template at render time.
        for key, value in kwds.items():
            if not isinstance(value, str):
                kwds[key] = str(value)
        self._kwds = kwds

        # This is meant to be overwritten by renderers, so that self.pkg_manager can
        # be used in templates.
        self.pkg_manager = None

        # We cannot validate kwds immediately... The Renderer should not validate
        # immediately. It should validate only the installation method being used.
        self._set_kwds_as_attrs()

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._template}, **{self._kwds})"

    def validate_kwds(self):
        """Raise `TemplateKeywordArgumentError` if keyword arguments to template are
        invalid.
        """
        # Check that all required keywords were provided by user.
        req_keys_not_found = self.required_arguments.difference(self._kwds)
        if req_keys_not_found:
            raise TemplateKeywordArgumentError(
                "Missing required arguments: '{}'.".format(
                    "', '".join(req_keys_not_found)
                )
            )

        # Check that unknown kwargs were not provided.
        all_kwds = self.required_arguments.union(self.optional_arguments.keys())
        unknown_kwds = set(self._kwds).difference(all_kwds)
        if unknown_kwds:
            raise TemplateKeywordArgumentError(
                "Keyword argument provided is not specified in template: '{}'.".format(
                    "', '".join(unknown_kwds)
                )
            )
        # Check that version is valid.
        if "version" in self.required_arguments:
            # At this point, we are certain "version" has been provided.
            v = self._kwds["version"]
            # Templates for builds from source have versions `{"ANY"}` because they can
            # ideally build any version.
            if (
                v not in self.versions
                # This indicates a source method.
                and self.versions != {"ANY"}
                # The presence of * in the list of binary urls indicates that any
                # version is allowed. It also suggests that the version passed by
                # the user is substituted into the URL for the binaries.
                # TODO: consider changing {"ANY"} to "*" in source methods.
                and "*" not in self.versions
            ):
                raise TemplateKeywordArgumentError(
                    "Unknown version '{}'. Allowed versions are '{}'.".format(
                        v, "', '".join(self.versions)
                    )
                )

    def _set_kwds_as_attrs(self):
        # Check that keywords do not shadow attributes of this object.
        shadowed = set(self._kwds).intersection(dir(self))
        if shadowed:
            raise TemplateKeywordArgumentError(
                "Invalid keyword arguments: '{}'. If these keywords are used by the"
                " template, then the template must be modified to use different"
                " keywords.".format("', '".join(shadowed))
            )
        # Set optional arguments to their default value, if the argument was not
        # provided.
        for k, v in self.optional_arguments.items():
            self._kwds.setdefault(k, v)
        # Set keywords as attributes to this object. This makes it easy to render
        # variables in the jinja template.
        for k, v in self._kwds.items():
            setattr(self, k, v)

    @property
    def template(self):
        return self._template

    @property
    def env(self) -> ty.Mapping[str, str]:
        return self._template.get("env", {})

    @property
    def instructions(self) -> str:
        return self._template.get("instructions", "")

    @property
    def arguments(self) -> ty.Mapping:
        return self._template.get("arguments", {})

    @property
    def required_arguments(self) -> ty.Set[str]:
        args = self.arguments.get("required", None)
        return set(args) if args is not None else set()

    @property
    def optional_arguments(self) -> ty.Dict[str, str]:
        args = self.arguments.get("optional", None)
        return args if args is not None else {}

    @property
    def versions(self) -> ty.Set[str]:
        raise NotImplementedError()

    def dependencies(self, pkg_manager: str) -> ty.List[str]:
        deps_dict = self._template.get("dependencies", {})
        # TODO: not sure why the following line raises a type error in mypy.
        return deps_dict.get(pkg_manager, [])  # type: ignore

    def install(self, pkgs: ty.List[str], opts: str = None) -> str:
        raise NotImplementedError(
            "This method is meant to be patched by renderer objects, so it can be used"
            " in templates and have access to the pkg_manager being used."
        )

    def install_dependencies(self, opts: str = None) -> str:
        raise NotImplementedError(
            "This method is meant to be patched by renderer objects, so it can be used"
            " in templates and have access to the pkg_manager being used."
        )


class _BinariesTemplate(_BaseInstallationTemplate):
    def __init__(self, template: _BinariesTemplateType, **kwds: str):
        super().__init__(template=template, **kwds)

    @property
    def urls(self) -> ty.Mapping[str, str]:
        # TODO: how can the code be changed so this cast is not necessary?
        self._template = ty.cast(_BinariesTemplateType, self._template)
        return self._template.get("urls", {})

    @property
    def versions(self) -> ty.Set[str]:
        # TODO: how can the code be changed so this cast is not necessary?
        self._template = ty.cast(_BinariesTemplateType, self._template)
        return set(self.urls.keys())


class _SourceTemplate(_BaseInstallationTemplate):
    def __init__(self, template: _SourceTemplateType, **kwds: str):
        super().__init__(template=template, **kwds)

    @property
    def versions(self) -> ty.Set[str]:
        return {"ANY"}
