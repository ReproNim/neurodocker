"""Tests for neurodocker.main"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

import sys

import pytest

from neurodocker.neurodocker import (create_parser, parse_args,
                                     convert_args_to_specs, main)


def test_parse_args():
    parser = create_parser()
    assert parser

    base_args = "generate {}"

    with pytest.raises(SystemExit):
        parse_args(base_args.format('').split())

    with pytest.raises(SystemExit):
        parse_args(base_args.format('-b').split())

    with pytest.raises(SystemExit):
        parse_args(base_args.format('-p').split())

    iter_args = ['--ants', '--fsl', '--miniconda', '--spm']
    for a in iter_args:
        with pytest.raises(SystemExit):
            parse_args(base_args.format(a).split())

    base_args = "generate -b ubuntu:17.04 -p apt --no-check-urls".split()
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

    args = base_args + ['--neurodebian', 'os_codename=zesty',
                        'download_server=usa-nh']
    namespace = parse_args(args)
    assert namespace.neurodebian

    args = base_args + ['--spm', 'version=12']
    namespace = parse_args(args)
    assert namespace.spm

    args = base_args + ['--instruction', 'RUN ls']
    namespace = parse_args(args)
    assert namespace.instruction
    assert isinstance(namespace.instruction, list)

    args = base_args + ['--no-check-urls']
    namespace = parse_args(args)
    assert not namespace.check_urls


def test_convert_args_to_specs():
    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'version=2.1.0',
            '--fsl', 'version=5.0.10',
            '--miniconda', 'conda_install=pandas,traits',
            '--mrtrix3',
            '--neurodebian', 'os_codename=zesty', 'download_server=usa-nh',
            '--spm', 'version=12',
            '--instruction', 'RUN ls',
            '--instruction', 'WORKDIR /home',
            '--no-check-urls']
    namespace = parse_args(args)
    assert namespace

    specs = convert_args_to_specs(namespace)
    assert vars(namespace).keys() == specs.keys()

    assert "," not in specs['miniconda']['conda_install']

    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'option']
    namespace = parse_args(args)
    with pytest.raises(ValueError):
        convert_args_to_specs(namespace)

    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'option=']
    namespace = parse_args(args)
    with pytest.raises(ValueError):
        convert_args_to_specs(namespace)

    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'use_binaries=false',
            '--mrtrix3', 'use_binaries=0']
    namespace = parse_args(args)
    specs = convert_args_to_specs(namespace)
    assert specs['ants']['use_binaries'] is False
    assert specs['mrtrix3']['use_binaries'] is False

    args = ['generate', '-b', 'ubuntu:17.04', '-p', 'apt',
            '--ants', 'use_binaries=true',
            '--mrtrix3', 'use_binaries=1']
    namespace = parse_args(args)
    specs = convert_args_to_specs(namespace)
    assert specs['ants']['use_binaries'] is True
    assert specs['mrtrix3']['use_binaries'] is True


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
