"""Tests for neurodocker.main"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals

import sys

import pytest

from neurodocker.neurodocker import create_parser, parse_args, main


def test_generate():
    args = ("generate -b ubuntu:17.04 -p apt"
            " --afni version=latest"
            " --ants version=2.2.0"
            " --freesurfer version=6.0.0"
            " --fsl version=5.0.10"
            " --user=neuro"
            " --miniconda env_name=neuro python_version=3.6"
            " --user=root"
            " --mrtrix3"
            " --neurodebian os_codename=zesty download_server=usa-nh"
            " --spm version=12 matlab_version=R2017a"
            " --no-check-urls"
            " --expose 1234 9000"
            " --copy relpath/to/file.txt /tmp/file.txt"
            " --add relpath/to/file2.txt /tmp/file2.txt"
            " --workdir /home"
            " --install git"
            " --user=neuro"
            )
    main(args.split())

    with pytest.raises(SystemExit):
        args = "-b ubuntu"
        main(args.split())

    with pytest.raises(SystemExit):
        args = "-p apt"
        main(args.split())

    with pytest.raises(SystemExit):
        main()

    args = "generate -b ubuntu -p apt --ants option=value"
    with pytest.raises(ValueError):
        main(args.split())


def test_generate_opts(capsys):
    args = "generate -b ubuntu:17.04 -p apt --no-check-urls {}"
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
    assert 'ENV KEY="VAL" \\' in out
    assert '  KEY2="VAL"' in out

    main(args.format('--expose 1230 1231').split())
    out, _ = capsys.readouterr()
    assert "EXPOSE 1230 1231" in out

    main(args.format('--workdir /home').split())
    out, _ = capsys.readouterr()
    assert "WORKDIR /home" in out

    main(args.format('--install git').split())
    out, _ = capsys.readouterr()
    assert "git" in out

    main(args.format('--instruction RUNecho').split())
    out, _ = capsys.readouterr()
    assert "RUNecho" in out


def test_generate_no_print(capsys):
    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt', '--no-check-urls']
    main(args)
    out, _ = capsys.readouterr()
    assert "FROM" in out and "RUN" in out

    args.append('--no-print-df')
    main(args)
    out, _ = capsys.readouterr()
    assert not out


def test_generate_save(tmpdir):
    outfile = tmpdir.join("test.txt")
    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt', '--mrtrix3',
            'use_binaries=false', '--no-print-df', '-o', outfile.strpath,
            '--no-check-urls']
    main(args)
    assert outfile.read(), "saved Dockerfile is empty"
    assert "git clone https://github.com/MRtrix3/mrtrix3.git" in outfile.read()
