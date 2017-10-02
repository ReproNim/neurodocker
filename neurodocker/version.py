"""This file defines the version of neurodocker.

Copied from https://github.com/nipy/nipype/blob/master/nipype/info.py.
"""

__version__ = '0.3.1'


def get_gitversion():
    """Neurodocker version as reported by `git describe`.

    Returns
    -------
    None or str
        Version of neurodocker according to git.
    """
    import os
    import subprocess

    here = os.path.dirname(os.path.realpath(__file__))

    try:
        cmd = 'git describe'.split()
        stdout, stderr = subprocess.Popen(cmd, cwd=here,
                                          stdout=subprocess.PIPE,
                                          stderr=subprocess.PIPE).communicate()
        ver = stdout.decode().strip()
    except Exception:
        ver = None

    return ver


gitversion = get_gitversion()
if gitversion:
    __version__ = gitversion
    if gitversion.startswith('v'):
        __version__ = __version__[1:]
