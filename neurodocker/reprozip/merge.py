"""Merge multiple ReproZip version 2 pack files.

This implementation makes several assumptions about the ReproZip traces. Please
do not use this as a general pack file merger.

Important note
--------------
The ouptut config.yml file is not created by merging the original config.yml
files. This file (created with `reprozip combine`) will inherit traits of the
machine on which it is running. Specifically, the architecture, distribution,
hostname, system, group ID, and user ID will all come from the local machine
and will not be taken from the original config.yml files. This script modifies
the combined config.yml file to use the distribution from the first run of the
first config.yml file.

Assumptions
-----------
- Pack files are version 2.
- All traces were run on the same distribution (e.g., debian stretch).
- If the same files exist in different traces, the contents of those files are
  identical.
"""
from glob import glob
import logging
import os
import tarfile
import tempfile

logger = logging.getLogger(__name__)


def _check_deps():
    """Raise RuntimeError if a dependency is not found. These dependencies are
    not included in `requirements.txt`.
    """
    import shutil

    msg = "Dependency '{}' not found."

    if shutil.which('rsync') is None:
        raise RuntimeError(msg.format('rsync'))
    try:
        import reprozip
    except Exception:
        raise RuntimeError(msg.format('reprozip'))


def _extract_rpz(rpz_path, out_dir):
    """Unpack .rpz file (tar archive) and the DATA.tar.gz file inside it."""
    basename = os.path.basename(rpz_path)
    prefix = "{}-".format(basename)
    path = tempfile.mkdtemp(prefix=prefix, dir=out_dir)

    with tarfile.open(rpz_path, 'r:*') as tar:
        tar.extractall(path)

    data_path = os.path.join(path, 'DATA.tar.gz')
    with tarfile.open(data_path, 'r:*') as tar:
        tar.extractall(path)


def _merge_data_dirs(data_dirs, merged_dest):
    """Merge data directories using `rsync`, and tar.gz the output."""
    import subprocess

    tmp_dest = tempfile.mkdtemp(prefix="reprozip-data")
    data_dirs = ' '.join(data_dirs)
    merge_cmd = ("rsync -rqabuP {srcs} {dest}"
                 "".format(srcs=data_dirs, dest=tmp_dest))
    subprocess.run(merge_cmd, shell=True, check=True)

    data_tar = os.path.join(merged_dest, 'DATA.tar.gz')
    with tarfile.open(data_tar, 'w:gz') as tar:
        tar.add(tmp_dest, arcname="")


def _get_distribution(filepath):
    """Return Linux distribution from the first run of a config.yml file."""
    import yaml

    with open(filepath, 'r') as fp:
        config = yaml.load(fp)

    return config['runs'][0]['distribution']


def _fix_config_yml(filepath, distribution):
    """Comment out 'additional_patterns', and replace the distribution of the
    local machine with `distribution`.
    """
    with open(filepath) as fp:
        config = fp.readlines()

    for ii, line in enumerate(config):
        if line.startswith('additional_patterns'):
            config[ii] = "# " + line
        if 'distribution:' in line:
            pre = line.split(':')[0]
            config[ii] = "{}: {}\n".format(pre, distribution)

    with open(filepath, 'w') as fp:
        for line in config:
            fp.write(line)


class _Namespace:
    # Replicates argparse namespace.
    # https://stackoverflow.com/a/28345836/5666087
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


def _combine_traces(traces, out_dir):
    """Run `reprozip combine` to combine trace databases and create new
    config.yml file.

    Important note: the config.yml file lists the local machine's architecture,
    distribution, hostname and system, and the current group id and user id.
    For best results, this should be run on the same machine as the traces.
    """
    from reprozip.main import combine

    args = _Namespace(traces=traces, dir=out_dir, identify_packages=False,
                      find_inputs_outputs=False)
    combine(args)

    original_config = os.path.join(os.path.dirname(traces[0]), 'config.yml')
    distribution = _get_distribution(original_config)

    config_filepath = os.path.join(out_dir, 'config.yml')
    _fix_config_yml(config_filepath, distribution)


def _write_version2_file(merged_dest):
    path = os.path.join(merged_dest, "METADATA", 'version')
    with open(path, 'w') as fp:
        fp.write("REPROZIP VERSION 2\n")


def _create_rpz(path, outfile):
    """Create a .rpz file from a `path` that contains METADATA and DATA.tar.gz.
    """
    data = os.path.join(path, 'DATA.tar.gz')
    metadata = os.path.join(path, 'METADATA')

    with tarfile.open(outfile, 'w:') as tar:
        tar.add(data, arcname='DATA.tar.gz')
        tar.add(metadata, arcname='METADATA')


def merge_pack_files(outfile, packfiles):
    """Merge reprozip version 2 pack files.

    This implementation has limitations. It uses rsync to merge the directories
    in different reprozip pack files, and does not take into account that files
    might have the same name but different contents.
    """
    if len(packfiles) < 2:
        raise ValueError("At least two packfiles are required.")

    _check_deps()

    if not outfile.endswith('.rpz'):
        logger.info("Adding '.rpz' extension to output file.")
        outfile += '.rpz'

    for pf in packfiles:
        if not os.path.isfile(pf):
            raise ValueError("File not found: {}".format(pf))

    tmp_dest = tempfile.mkdtemp(prefix="neurodocker-reprozip-merge-")
    merged_dest = os.path.join(tmp_dest, "merged")
    merged_dest_metadata = os.path.join(merged_dest, "METADATA")
    os.makedirs(merged_dest_metadata)

    for this_rpz in packfiles:
        logger.info("Extracting {}".format(this_rpz))
        _extract_rpz(this_rpz, tmp_dest)

    logger.info("Merging DATA directories")
    data_dirs_pattern = os.path.abspath(os.path.join(tmp_dest, "**", "DATA"))
    data_dirs = glob(data_dirs_pattern)
    _merge_data_dirs(data_dirs, merged_dest)

    logger.info("Merging traces and creating new config.yml")
    traces_pattern = os.path.join(tmp_dest, "**", "METADATA", "trace.sqlite3")
    traces = glob(traces_pattern)
    _combine_traces(traces=traces, out_dir=merged_dest_metadata)

    _write_version2_file(merged_dest)
    logger.info("Creating merged pack file")
    _create_rpz(merged_dest, outfile)
