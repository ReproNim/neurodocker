""""""

from collections import OrderedDict
import inspect

from neurodocker.generators.common import _installation_implementations


class _SingularityRecipeImplementations:

    def __init__(self, singularity_recipe_object):
        self._singobj = singularity_recipe_object

    def base(self, base):
        if base.startswith('docker://'):
            bootstrap = 'docker'
            from_ = base.split('docker://', 1)[1]
        elif base.startswith('shub://'):
            bootstrap = 'shub'
            from_ = base.split('shub://', 1)[1]
        else:
            raise ValueError(
                "singularity base must be in the form `docker://...` or"
                " `shub://...`"
            )
        self._singobj._header['Bootstrap'] = bootstrap
        self._singobj._header['From'] = from_

    def copy(self, list_srcs_dest):
        self._singobj._files.append(list_srcs_dest)

    def entrypoint(self, entrypoint):
        self._singobj._runscript.append(entrypoint)

    def env(self, d):
        self._singobj._environment.update(**d)


class SingularityRecipe:

    def __init__(self, specs):
        self._specs = specs

        self._header = OrderedDict()
        self._help = []
        self._setup = []
        self._post = []
        self._environment = OrderedDict()
        self._files = []
        self._runscript = []
        self._test = []
        self._labels = []

        self._implementations = {
            **_installation_implementations,
            **dict(inspect.getmembers(_SingularityRecipeImplementations(self),
                                      predicate=inspect.ismethod))
        }

        self._order = (
            ('header', self._header),
            ('help', self._help),
            ('setup', self._setup),
            ('post', self._post),
            ('environment', self._environment),
            ('files', self._files),
            ('runscript', self._runscript),
            ('test', self._test),
            ('labels', self._labels)
        )
        self._parts_filled = False
        self._add_neurodocker_header()

    def render(self):
        def _render_one(section):
            renderer = getattr(self, "_render_{}".format(section))
            return renderer()

        if not self._parts_filled:
            self._fill_parts()
        return "\n\n".join(
            map(_render_one, (sec for sec, con in self._order if con))
        )

    def _render_header(self):
        return "\n".join(
            "{}: {}".format(k, v) for k, v in self._header.items()
        )

    def _render_help(self):
        return "%help\n" + "\n".join(self._help)

    def _render_setup(self):
        return "%setup\n" + "\n".join(self._setup)

    def _render_post(self):
        return "%post\n" + "\n".join(self._post)

    def _render_environment(self):
        return ("%environment\n"
                + "\n".join("export {}={}".format(*kv)
                            for kv in self._environment.items()))

    def _render_files(self):
        return ("%files\n"
                + "\n".join("{} {}".format(*f) for f in self._files))

    def _render_runscript(self):
        return "%runscript\n" + "\n".join(self._runscript)

    def _render_test(self):
        return "%test\n" + "\n".join(self._test)

    def _render_labels(self):
        return "%labels\n" + "\n".join(self._labels)

    def _add_neurodocker_header(self):
        self._specs['instructions'].insert(1, ('_header', {'version': 'generic', 'method': 'custom'}))
        # interface = _Header(
        #     'generic', pkg_manager=self._specs['pkg_manager'], method='custom'
        # )
        # self._post.append(interface.render_run())
        # self._environment.update(**interface.render_env())

    def _fill_parts(self):
        pkg_man = self._specs['pkg_manager']
        for item in self._specs['instructions']:
            instruction, params = item
            if instruction in self._implementations.keys():
                impl = self._implementations[instruction]
                if impl in _installation_implementations.values():
                    interface = impl(pkg_manager=pkg_man, **params)
                    if interface.env:
                        self._environment.update(**interface.render_env())
                    if interface.run:
                        self._post.append(interface.render_run())
                else:
                    impl(params)
            else:
                raise ValueError(
                    "instruction not understood: '{}'".format(instruction)
                )
        self._parts_filled = True