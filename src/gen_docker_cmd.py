import os

# start with the basics
script_types = {'py': 'python',
                'sh': '/bin/bash'}

class DockerCommand(object):

    def __init__(self, image, script=None, cmdline=None, script_args=None,
                 mount=None):
        self.image = image
        self.cmdline = cmdline
        self.script = script
        self.script_args = script_args
        self.mount = mount
        self._cmd = 'docker run -t {}'.format(self.image)

    def _is_valid_cmd(self):
        """ Ensure only one command is run """
        if not self.script and not self.cmdline:
            raise AttributeError('DockerCommand missing required arg')
        elif self.script and self.cmdline:
            raise AttributeError(
            'DockerCommand cannot accept multiple executables')

    def _is_valid_script(self):
        if not os.path.exists(self.script):
            raise IOError('{} not found'.format(self.script))

    def _is_valid_mnt(self):
        local, mnt = self.split(':')
        if not os.path.exists(local):

    def add_mount(self):
        if ':' not in self.mount:
            raise AttributeError(
            'Mount must include target inside docker image.')
        self._is_valid_mnt()
        return ' -v {}'.format(os.path.abspath(self.mount))

    def add_src(self, src):
        return ' {}'.format(src)

    def composite_cmd(self):
        self._is_valid_cmd()
        if self.mount:
            self._cmd += self.add_mount()

        if self.cmdline:
            self._cmd += self.add_src(self.cmdline)
        elif self.script:
            suffix = self.script.split('.')[-1]
            if suffix in script_types:
                prefix = script_types[suffix]
            else:
                raise Exception(
                "Only scripts ending in {} are currently supported".format(
                str(list(script_types))))
            self._cmd += self.add_src(prefix + ' ' + self.script)
            if self.script_args:
                self._cmd += self.add_src(self.script_args)
        return self._cmd
