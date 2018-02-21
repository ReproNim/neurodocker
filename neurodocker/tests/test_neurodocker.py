"""Tests for neurodocker.main"""
# Author: Jakub Kaczmarzyk <jakubk@mit.edu>

from __future__ import absolute_import, unicode_literals

import pytest

from neurodocker.neurodocker import main


def test_generate():
    args = ("generate docker -b ubuntu:17.04 -p apt"
            " --arg FOO=BAR BAZ"
            " --afni version=latest"
            " --ants version=2.2.0"
            " --freesurfer version=6.0.0"
            " --fsl version=5.0.10"
            " --user=neuro"
            " --miniconda env_name=neuro conda_install=python=3.6.2"
            " --user=root"
            " --mrtrix3 version=3.0"
            " --neurodebian os_codename=zesty download_server=usa-nh"
            " --spm version=12 matlab_version=R2017a"
            " --expose 1234 9000"
            " --volume /var /usr/bin"
            " --label FOO=BAR BAZ=CAT"
            " --copy relpath/to/file.txt /tmp/file.txt"
            " --add relpath/to/file2.txt /tmp/file2.txt"
            " --cmd '--arg1' '--arg2'"
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
    assert 'ENV KEY="VAL" \\' in out
    assert '  KEY2="VAL"' in out

    main(args.format('--expose 1230 1231').split())
    out, _ = capsys.readouterr()
    assert "EXPOSE 1230 1231" in out

    main(args.format('--workdir /home').split())
    out, _ = capsys.readouterr()
    assert "WORKDIR /home" in out

    main(args.format('--install vi').split())
    out, _ = capsys.readouterr()
    assert "vi" in out


@pytest.mark.xfail
def test_generate_from_json(capsys, tmpdir):
    import json

    cmd = "generate docker -b debian:stretch -p apt --c3d version=1.0.0"
    main(cmd.split())
    true, _ = capsys.readouterr()

    specs = {'generation_timestamp': '2017-08-31 21:49:04',
             'instructions': [['base', 'debian:stretch'],
                              ['c3d', {'version': '1.0.0'}]],
             'neurodocker_version': '0.2.0-18-g9227b17',
             'pkg_manager': 'apt'}
    str_specs = json.dumps(specs)
    filepath = tmpdir.join("specs.json")
    filepath.write(str_specs)

    gen_cmd = "generate --file {}".format(filepath)
    main(gen_cmd.split())
    test, _ = capsys.readouterr()

    # These indices chop off the header (with timestamp) and the layer that
    # saves to JSON (with timestamp).
    sl = slice(8, -19)
    assert true.split('\n')[sl] == test.split('\n')[sl]


def test_generate_no_print(capsys):
    args = ['generate', 'docker', '-b', 'ubuntu:17.04', '-p', 'apt']
    main(args)
    out, _ = capsys.readouterr()
    assert "FROM" in out and "RUN" in out

    args.append('--no-print-df')
    main(args)
    out, _ = capsys.readouterr()
    assert not out
