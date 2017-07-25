"""Tests for neurodocker.main"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

import sys

import pytest

from neurodocker.neurodocker import create_parser, parse_args, main

# TODO: write tests for parse_args

def test_main():
    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'version=2.1.0',
            '--fsl', 'version=5.0.10',
            '--miniconda', 'python_version=3.5.1',
            '--mrtrix3',
            '--neurodebian', 'os_codename=zesty', 'download_server=usa-nh',
            '--spm', 'version=12', 'matlab_version=R2017a',
            '--no-check-urls']
    main(args)

    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt', '--no-check-urls']
    main(args)

    with pytest.raises(SystemExit):
        args = ['-b', 'ubuntu:17.04']
        main(args)

    with pytest.raises(SystemExit):
        main()

    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'option=value']
    with pytest.raises(ValueError):
        main(args)

def test_dockerfile_opts(capsys):
    args = "generate -b ubuntu:17.04 -p apt --no-check-urls {}"
    main(args.format('--user=neuro').split())
    out, _ = capsys.readouterr()
    assert "USER neuro" in out

    main(args.format('--env KEY=VAL KEY2=VAL').split())
    out, _ = capsys.readouterr()
    assert "ENV KEY=VAL \\" in out
    assert "  KEY2=VAL" in out

    main(args.format('--port 1230 1231').split())
    out, _ = capsys.readouterr()
    assert "EXPOSE 1230 1231" in out

def test_no_print(capsys):
    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt', '--no-check-urls']
    main(args)
    out, _ = capsys.readouterr()
    assert "FROM" in out and "RUN" in out

    args.append('--no-print-df')
    main(args)
    out, _ = capsys.readouterr()
    assert not out


def test_save(tmpdir):
    outfile = tmpdir.join("test.txt")
    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt', '--mrtrix3',
            'use_binaries=false', '--no-print-df', '-o', outfile.strpath,
            '--no-check-urls']
    main(args)
    assert outfile.read(), "saved Dockerfile is empty"
    assert "git clone https://github.com/MRtrix3/mrtrix3.git" in outfile.read()
