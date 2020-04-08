""""""

from collections import OrderedDict
import copy
import inspect
import logging

from neurodocker.generators.common import _add_to_entrypoint
from neurodocker.generators.common import _get_json_spec_str
from neurodocker.generators.common import _installation_implementations
from neurodocker.generators.common import _install
from neurodocker.generators.common import _Users
from neurodocker.generators.common import ContainerSpecGenerator
from neurodocker.generators.common import NEURODOCKER_ENTRYPOINT

logger = logging.getLogger(__name__)


class _SingularityRecipeImplementations:
    def __init__(self, singularity_recipe_object):
        self._singobj = singularity_recipe_object

    def add_to_entrypoint(self, cmd):
        self._singobj._post.append(_add_to_entrypoint(cmd))

    def base(self, base):
        if base.startswith('docker://'):
            bootstrap = 'docker'
            from_ = base.split('docker://', 1)[1]
        elif base.startswith('shub://'):
            bootstrap = 'shub'
            from_ = base.split('shub://', 1)[1]
        # If no prefix given, assume base is a Docker image.
        else:
            bootstrap = 'docker'
            from_ = base

        self._singobj._header['Bootstrap'] = bootstrap
        self._singobj._header['From'] = from_

    def copy(self, list_srcs_dest):
        self._singobj._files.append(list_srcs_dest)

    def install(self, pkgs, pkg_manager, opts=None):
        self._singobj._post.append(_install(pkgs, pkg_manager))

    def entrypoint(self, entrypoint):
        self._singobj._runscript = entrypoint

    def env(self, d):
        self._singobj._environment.extend(d.items())

    def run(self, s):
        self._singobj._post.append(s)

    def run_bash(self, s):
        s = "bash -c '{}'".format(s)
        self.run(s)

    def user(self, user):
        user_cmd = "su - {}".format(user)
        add_user_cmd = _Users.add(user)
        if add_user_cmd:
            cmd = add_user_cmd + "\n" + user_cmd
        else:
            cmd = user_cmd
        self._singobj._post.append(cmd)

    def workdir(self, path):
        self._singobj._post.append("cd {}".format(path))


class SingularityRecipe(ContainerSpecGenerator):
    def __init__(self, specs):
        self._specs = copy.deepcopy(specs)

        self._header = OrderedDict()
        self._help = []
        self._setup = []
        self._post = []
        self._environment = []
        self._files = []
        self._runscript = '/neurodocker/startup.sh "$@"'
        self._test = []
        self._labels = []

        self._implementations = {
            **_installation_implementations,
            **dict(
                inspect.getmembers(
                    _SingularityRecipeImplementations(self),
                    predicate=inspect.ismethod))
        }

        self._order = (('header', self._header), ('help', self._help),
                       ('setup', self._setup), ('post', self._post),
                       ('environment', self._environment), ('files',
                                                            self._files),
                       ('runscript',
                        self._runscript), ('test', self._test), ('labels',
                                                                 self._labels))
        self._parts_filled = False
        _Users.clear_memory()
        self._add_neurodocker_header()
        self._add_json()

        self._rendered = False

    def render(self):
        def _render_one(section):
            renderer = getattr(self, "_render_{}".format(section))
            return renderer()

        if not self._parts_filled:
            self._fill_parts()

        if not self._rendered:
            self._rendered = self.commented_header + "\n\n".join(
                map(_render_one, (sec for sec, con in self._order if con)))
        return self._rendered

    def _render_header(self):
        return "\n".join(
            "{}: {}".format(k, v) for k, v in self._header.items())

    def _render_help(self):
        return "%help\n" + "\n".join(self._help)

    def _render_setup(self):
        return "%setup\n" + "\n".join(self._setup)

    def _render_post(self):
        return "%post\n" + "\n\n".join(self._post)

    def _render_environment(self):
        return ("%environment\n" + "\n".join('export {}="{}"'.format(*kv)
                                             for kv in self._environment))

    def _render_files(self):
        return ("%files\n" + "\n".join("{} {}".format(*f)
                                       for f in self._files))

    def _render_runscript(self):
        return "%runscript\n" + self._runscript

    def _render_test(self):
        return "%test\n" + "\n".join(self._test)

    def _render_labels(self):
        return "%labels\n" + "\n".join(self._labels)

    def _add_neurodocker_header(self):
        kwds = {'version': 'generic', 'method': 'custom'}
        # If ndfreeze is requested, put it before the neurodocker header.
        offset = 0
        if len(self._specs['instructions']) > 1:
            if self._specs['instructions'][1][0] == 'ndfreeze':
                offset = 1
        self._specs['instructions'].insert(1 + offset, ('_header', kwds))
        self._specs['instructions'].insert(1 + offset, ('user', 'root'))


    def _fill_parts(self):
        pkg_man = self._specs['pkg_manager']
        for item in self._specs['instructions']:
            instruction, params = item
            if instruction in self._implementations.keys():
                impl = self._implementations[instruction]
                if impl in _installation_implementations.values():
                    try:
                        interface = impl(pkg_manager=pkg_man, **params)
                    except Exception as exc:
                        logger.error("Failed to instantiate {}: {}".format(
                            impl, exc))
                        raise
                    if interface.env:
                        _this_env = interface.render_env()
                        if _this_env is not None:
                            self._environment.extend(_this_env.items())
                    if interface.run:
                        self._post.append(interface.render_run())
                else:
                    if instruction == 'install':
                        impl(params, pkg_manager=pkg_man)
                    else:
                        impl(params)
            else:
                raise ValueError(
                    "instruction not understood: '{}'".format(instruction))
        if not self._runscript:
            self._runscript = NEURODOCKER_ENTRYPOINT
        self._parts_filled = True

    def _add_json(self):
        jsonstr = _get_json_spec_str(self._specs)
        self._specs['instructions'].append(("run", jsonstr))
