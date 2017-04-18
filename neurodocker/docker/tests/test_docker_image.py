from __future__ import absolute_import
import os

import docker
import pytest

from src.docker import DockerImage, DockerContainer
from src.docker.ants import ANTs
from src.docker.fsl import FSL
from src.docker.spm import SPM

class TestBuildCompleteDockerImage(object):
    """Build a Docker image that includes all of the supported software.
    """
    @pytest.fixture(autouse=True)
    def setup(self, tmpdir):
        self.tmpdir = tmpdir
        self.client = docker.from_env()

        base_cmd = "FROM centos:7"
        pkg_manager = "yum"

        cmds = [base_cmd,
                ANTs('2.1.0', pkg_manager).cmd,
                FSL('5.0.8', pkg_manager, use_binaries=True).cmd,
                # SPM(12, 'R2017a', pkg_manager).cmd,
                ]
        self.full_dockerfile = '\n\n'.join(cmds)

        # Save Dockerfile.
        dockerfile_path = os.path.join(tmpdir.strpath, 'Dockerfile')
        with open(dockerfile_path, 'w') as fp:
            fp.write(self.full_dockerfile)

    def test_build_and_run(self):
        """Test building Docker image and running command within Docker
        container.
        """
        tag = "test:latest"
        log_path = os.path.join(self.tmpdir.strpath, 'TEST-latest.log')
        img = DockerImage(path=self.tmpdir.strpath, tag=tag)
        image = img.build_raw(filepath=log_path)

        container = DockerContainer(image)
        container.start()
        # "bash -c '$SPMMCRCMD'" should be tested, but it blocks. How do we get
        # around that?
        cmds = ["Atropos -h", "bet -h",]
        outputs = []
        for cmd in cmds:
            output = container.exec_run(cmd=cmd)
            outputs.append(output)
        container.cleanup(remove=True, force=True)

        outputs_str = ' '.join(outputs)
        assert "error:" not in outputs_str, "Error in command execution."
