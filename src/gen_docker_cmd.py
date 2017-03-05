import os

" image: {image} "
" command: {cmd} "
" volumes:
    "{abspath({local_mnt}): {"bind: 'abspath({docker})'",
                 "mode: 'optional'"}

class DockerCommand(object):
    """ """
    def __init__(self, image, cmd=None, volumes=[]):
        self.image = image
        self.cmd = cmd
        if self.volumes:
            self.volumes = self._fmt_vols()

    def _fmt_vols(self):
        volumes = {}
        for vol in self.volumes:
            local, mnt = vol.split(':')
            if os.path.exists(local):
                volumes[os.path.abspath(local)] = {"bind": mnt}
        return volumes
