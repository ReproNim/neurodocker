"""Tests for neurodocker.main"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

import sys

import pytest

from neurodocker.main import (create_parser, parse_args, convert_args_to_specs,
                              main)


def test_parse_args():
    parser = create_parser()
    assert parser

    with pytest.raises(SystemExit):
        parse_args([''])

    with pytest.raises(SystemExit):
        parse_args(['-b'])

    with pytest.raises(SystemExit):
        parse_args(['-p'])

    iter_args = ['--ants', '--fsl', '--miniconda', '--spm']
    for a in iter_args:
        with pytest.raises(SystemExit):
            parse_args([a])

    base_args = "-b ubuntu:17.04 -p apt --no-check-urls".split()
    namespace = parse_args(base_args)
    assert namespace.base
    assert namespace.pkg_manager
    assert not namespace.check_urls
    pkgs_present = (namespace.ants or namespace.fsl
                    or namespace.miniconda or namespace.spm)
    assert not pkgs_present

    args = base_args + ['--ants', 'version=2.1.0']
    namespace = parse_args(args)
    assert namespace.ants

    args = base_args + ['--fsl', 'version=5.0.10']
    namespace = parse_args(args)
    assert namespace.fsl

    args = base_args + ['--miniconda', 'conda_install=pandas,traits']
    namespace = parse_args(args)
    assert namespace.miniconda

    args = base_args + ['--spm', 'version=12']
    namespace = parse_args(args)
    assert namespace.spm

    args = base_args + ['--no-check-urls']
    namespace = parse_args(args)
    assert not namespace.check_urls


def test_convert_args_to_specs():

    args = ['-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'version=2.1.0',
            '--fsl', 'version=5.0.10',
            '--miniconda', 'conda_install=pandas,traits',
            '--spm', 'version=12',
            '--no-check-urls']
    namespace = parse_args(args)
    assert namespace

    specs = convert_args_to_specs(namespace)
    assert vars(namespace).keys() == specs.keys()

    assert "," not in specs['miniconda']['conda_install']


def test_main():
    args = ['-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'version=2.1.0',
            '--fsl', 'version=5.0.10',
            '--miniconda', 'python_version=3.5.1',
            '--spm', 'version=12', 'matlab_version=R2017a',
            '--no-check-urls']
    main(args)

    args = ['-b', 'ubuntu:17.04', '-p', 'apt', '--no-check-urls']
    main(args)

    with pytest.raises(SystemExit):
        args = ['-b', 'ubuntu:17.04']
        main(args)

    with pytest.raises(SystemExit):
        main()


def test_no_print(capsys):
    args = ['-b', 'ubuntu:17.04', '-p', 'apt', '--no-check-urls']
    main(args)
    out, err = capsys.readouterr()
    assert "FROM" in out and "RUN" in out

    args.append('--no-print-df')
    main(args)
    out, err = capsys.readouterr()
    assert not out



def test_save(tmpdir):
    outfile = tmpdir.join("test.txt")
    args = ['-b', 'ubuntu:17.04', '-p', 'apt', '--no-print-df', '-o',
            outfile.strpath, '--no-check-urls']
    main(args)
    assert outfile.read()
