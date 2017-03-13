"""Tests for src.docker.dockerfile.Dockerfile

To run on command-line: python -m pytest path/to/nipype-regtests/src/
"""
from __future__ import absolute_import, division, print_function
from copy import deepcopy

import pytest

from src.docker.dockerfile import Dockerfile

specs = {
    "base": "ubuntu:16.04",
    "conda-env": {
        "dependencies": [
            "python=3.5.1",
            "numpy",
            {"pip": "pandas"}
        ]
    }
}

cmds_list = [
    'FROM ubuntu:16.04',
    '# Get dependencies.\nRUN apt-get update && apt-get install -y --no-install-recommends \\\n    bzip2 \\\n    ca-certificates \\\n    curl',
    '# Install Miniconda, and create Conda environment from file.\nRUN curl -sSLO https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh && \\\n    /bin/bash Miniconda3-latest-Linux-x86_64.sh -b -p /usr/local/miniconda  && \\\n    rm Miniconda3-latest-Linux-x86_64.sh\nENV CONDAPATH=/usr/local/miniconda/bin \\\n    LANG=C.UTF-8 \\\n    LC_ALL=C.UTF-8\nCOPY conda-env.yml /home/conda-env.yml\nRUN $CONDAPATH/conda update -y conda && \\\n    $CONDAPATH/conda env create -f /home/conda-env.yml -n new_env && \\\n    cd $CONDAPATH/../ && rm -rf conda-meta include share ssl && \\\n    $CONDAPATH/conda clean -y -a\nENV PATH=/usr/local/miniconda/envs/new_env/bin:$PATH'
]


class TestDockerfile(object):
    """Test src.docker.dockerfile.Dockerfile

    TODO
    ----
    - Split method _get_instructs_and_deps() and add relevant tests.
    - Clean up `cmds_list`, above.
    """
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.dfile = Dockerfile(specs=specs, savedir=tmpdir.strpath,
                                deps_method='apt-get')

    def test_add_instruction(self):
        cmd = "RUN echo Hello, World!"
        cmds_pre = deepcopy(self.dfile._cmds)  # Make a copy.
        self.dfile.add_instruction(cmd)
        cmds_post = deepcopy(self.dfile._cmds)  # Make a copy.
        assert len(cmds_post) == len(cmds_pre)+1, "Error appending command."
        assert  cmds_post == cmds_pre + [cmd], "Error appending command."
        self.dfile._cmds = []  # Reset the list of commands.

    def test__add_base(self):
        self.dfile._add_base()
        assert self.dfile._cmds == ["FROM ubuntu:16.04"], "Error adding base image"

    def test_create(self):
        # Clear Dockerfile commands.
        self.dfile._cmds = []
        self.dfile.cmd = ""

        self.dfile.create()
        assert self.dfile._cmds == cmds_list, "Error creating list of commands."
        self.dfile._cmds = []  # Reset list of commands.

    def test_save(self):
        # Test that file will not be saved if there are no instructions.
        self.dfile.cmd = ""
        with pytest.raises(Exception):
            self.dfile.save()

        self.dfile.cmd = "FROM ubuntu:16.04"
        self.dfile.save()
        assert len(self.tmpdir.listdir()) == 1, "File not saved"

        file_content = self.tmpdir.join("Dockerfile").read()
        assert file_content == self.dfile.cmd, "Incorrect Dockerfile content"
