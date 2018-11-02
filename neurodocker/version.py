"""This file defines the version of neurodocker.

Copied from https://github.com/nipy/nipype/blob/master/nipype/info.py.
"""

__version__ = '0.4.2'


def get_gitversion():
    """Neurodocker version as reported by `git describe`.

    Returns
    -------
    None or str
        Version of neurodocker according to git.
    """
    import os
    import subprocess

    here = os.path.abspath(os.path.dirname(__file__))
    try:
        cmd = "git describe".split()
        return subprocess.check_output(
            cmd, cwd=here, stderr=subprocess.DEVNULL).decode().strip()
    except subprocess.CalledProcessError:
        return None


# Only append git hash if this is not a release.
if 'dev' in __version__:
    gitversion = get_gitversion()  # v0.3.2-183-gea5425b
    if gitversion is not None:
        __version__ = gitversion
        if gitversion.startswith('v'):
            __version__ = __version__[1:]
