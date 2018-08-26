"""Run the neurodocker examples and check for failures."""

import glob
import os
import subprocess

here = os.path.dirname(os.path.realpath(__file__))


def test_examples_readme():
    with open(os.path.join(here, "README.md")) as f:
        readme = f.read()

    readme = readme.replace("\\\n", " ")

    cmds = []
    for line in readme.splitlines():
        if not line.startswith("neurodocker generate"):
            continue
        s = line.split()
        if 'docker' in s[2] and 'singularity' in s[2]:
            s[2] = 'docker'
            cmds.append(" ".join(s))
            s[2] = 'singularity'
            cmds.append(" ".join(s))
        else:
            cmds.append(line)

    print("Testing {} commands from the examples README".format(len(cmds)))

    with TemporaryChDir(here):
        for c in cmds:
            subprocess.run(c, shell=True, check=True)


def test_specialized_examples():
    files = glob.glob(os.path.join(here, "**", "generate.sh"))
    print("Testing {} commands from specialized examples".format(len(files)))
    with TemporaryChDir(here):
        for f in files:
            subprocess.run(f, shell=True, check=True)


class TemporaryChDir:
    def __init__(self, wd):
        self.wd = wd
        self._wd_orig = os.getcwd()

    def __enter__(self):
        os.chdir(self.wd)

    def __exit__(self, exc_type, exc_value, tb):
        os.chdir(self._wd_orig)
