"""Tests for neurodocker.main"""

import json
import io

import pytest
from unittest import mock

from neurodocker.neurodocker import main


def test_generate():
    args = ("generate docker -b ubuntu:17.04 -p apt"
            " --arg FOO=BAR BAZ"
            " --ndfreeze date=20180312"
            " --afni version=latest method=source"
            " --ants version=2.2.0 method=source"
            " --freesurfer version=6.0.0"
            " --fsl version=5.0.10"
            " --user=neuro"
            " --miniconda create_env=neuro conda_install=python=3.6.2"
            " --user=root"
            " --mrtrix3 version=3.0_RC3"
            " --neurodebian os_codename=zesty server=usa-nh"
            " --spm12 version=r7219 matlab_version=R2017a"
            " --expose 1234 9000"
            " --volume /var /usr/bin"
            " --label FOO=BAR BAZ=CAT"
            " --copy relpath/to/file.txt /tmp/file.txt"
            " --add relpath/to/file2.txt /tmp/file2.txt"
            " --cmd '--arg1' '--arg2'"
            " --workdir /home"
            " --install git"
            " --user=neuro")
    main(args.split())

    with pytest.raises(SystemExit):
        args = "-b ubuntu"
        main(args.split())

    with pytest.raises(SystemExit):
        args = "-p apt"
        main(args.split())

    with pytest.raises(SystemExit):
        main()


def test_generate_opts(capsys):
    args = "generate docker -b ubuntu:17.04 -p apt {}"
    main(args.format('--user=neuro').split())
    out, _ = capsys.readouterr()
    assert "USER neuro" in out

    main(args.format('--add path/to/file.txt /tmp/file.txt').split())
    out, _ = capsys.readouterr()
    assert 'ADD ["path/to/file.txt", "/tmp/file.txt"]' in out

    main(args.format('--copy path/to/file.txt /tmp/file.txt').split())
    out, _ = capsys.readouterr()
    assert 'COPY ["path/to/file.txt", "/tmp/file.txt"]' in out

    main(args.format('--env KEY=VAL KEY2=VAL').split())
    out, _ = capsys.readouterr()
    assert (('ENV KEY="VAL" \\' in out and 'KEY="VAL"' in out)
            or ('ENV KEY2="VAL" \\' in out and 'KEY="VAL"'))

    main(args.format('--expose 1230 1231').split())
    out, _ = capsys.readouterr()
    assert "EXPOSE 1230 1231" in out

    main(args.format('--workdir /home').split())
    out, _ = capsys.readouterr()
    assert "WORKDIR /home" in out

    main(args.format('--install vi').split())
    out, _ = capsys.readouterr()
    assert "vi" in out

    # Test that nd_freeze comes before the header.
    main(args.format('--ndfreeze date=20180312').split())
    out, _ = capsys.readouterr()
    assert out.find("nd_freeze") < out.find("ND_ENTRYPOINT")

    with mock.patch("neurodocker.interfaces.Miniconda._installed", False):
        main(args.format('--miniconda create_env=newenv version=4.7.10 '
                         'conda_install=python=3.7').split())
    out, _ = capsys.readouterr()
    assert "https://repo.continuum.io/miniconda/Miniconda3-4.7.10-Linux-x86_64.sh" in out


def test_generate_from_json(capsys, tmpdir):
    cmd = "generate docker -b debian:stretch -p apt --convert3d version=1.0.0"
    main(cmd.split())
    true, _ = capsys.readouterr()

    specs = {
        'instructions': [['base', 'debian:stretch'],
                         ['convert3d', {
                             'version': '1.0.0'
                         }]],
        'pkg_manager':
        'apt'
    }
    str_specs = json.dumps(specs)
    filepath = tmpdir.join("specs.json")
    filepath.write(str_specs)

    gen_cmd = "generate docker {}".format(filepath)
    main(gen_cmd.split())
    test, _ = capsys.readouterr()

    # Remove last RUN instruction (it contains saving to JSON and order is not guaranteed).
    true = "RUN".join(true.split("RUN")[:-1])
    test = "RUN".join(test.split("RUN")[:-1])

    # Remove comments.
    true = [t for t in true.splitlines() if not t.startswith('#')]
    test = [t for t in test.splitlines() if not t.startswith('#')]

    assert true == test


def test_generate_from_json_stdin(capsys, monkeypatch):
    specs = {
        'instructions': [['base', 'debian:stretch'],
                         ['install', ['git', 'vim']]],
        'pkg_manager': 'apt',
    }
    monkeypatch.setattr('sys.stdin', io.StringIO(json.dumps(specs)))
    main("generate docker -".split())
    test, _ = capsys.readouterr()

    true_cmd = "generate docker -b debian:stretch -p apt --install git vim"
    main(true_cmd.split())
    true, _ = capsys.readouterr()

    # Remove last RUN instruction (it contains saving to JSON and order is not guaranteed).
    true = "RUN".join(true.split("RUN")[:-1])
    test = "RUN".join(test.split("RUN")[:-1])

    # Remove comments.
    true = [t for t in true.splitlines() if not t.startswith('#')]
    test = [t for t in test.splitlines() if not t.startswith('#')]

    assert true == test
