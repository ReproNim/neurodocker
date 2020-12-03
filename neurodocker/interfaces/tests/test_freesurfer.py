"""Tests for neurodocker.interfaces.FreeSurfer"""

from neurodocker.interfaces.tests import utils


class TestFreeSurfer(object):
    def test_docker(self):
        specs = {
            "pkg_manager": "apt",
            "instructions": [
                ("base", "ubuntu:20.04"),
                ("freesurfer", {"version": "7.1.1-min"}),
                ("user", "neuro"),
            ],
        }

        bash_test_file = "test_freesurfer.sh"
        utils.test_docker_container_from_specs(
            specs=specs, bash_test_file=bash_test_file
        )

    def test_singularity(self):
        specs = {
            "pkg_manager": "apt",
            "instructions": [
                ("base", "docker://ubuntu:20.04"),
                ("freesurfer", {"version": "7.1.1-min"}),
                ("user", "neuro"),
            ],
        }
        bash_test_file = "test_freesurfer.sh"
        utils.test_singularity_container_from_specs(
            specs=specs, bash_test_file=bash_test_file
        )
