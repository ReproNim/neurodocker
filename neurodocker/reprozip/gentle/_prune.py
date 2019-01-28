"""Remove all files under a directory but not caught by `reprozip trace`."""

from pathlib import Path

import yaml


def _in_docker():
    if not Path('/proc/1/cgroup').is_file():
        return False
    with open('/proc/1/cgroup') as f:
        return 'docker' in f.read() and Path('/.dockerenv').is_file()


def main(*, yaml_file, directories_to_prune):

    if not _in_docker():
        raise RuntimeError(
            "Not running in a Docker container. This script should only be"
            " used within a container.")

    yaml_file = Path(yaml_file)
    if yaml_file.name != 'config.yml':
        raise ValueError("File should be named `config.yml`")
    with yaml_file.open(mode='r') as f:
        config = yaml.load(f)

    # Paths caught by `reprozip trace`. These can be directories or files.
    # There could potentially be other information (e.g., input/output,
    # packages), but we are only interested in the contents of this key.
    files_to_keep = config['other_files']
    files_to_keep = {Path(p) for p in files_to_keep}

    if isinstance(directories_to_prune, (Path, str)):
        directories_to_prune = [directories_to_prune]

    directories_to_prune = [Path(d) for d in directories_to_prune]

    for d in directories_to_prune:
        if not d.is_dir():
            raise ValueError("Directory does not exist: {}".format(d))

    all_files = set()
    for d in directories_to_prune:
        all_files.update(Path(d).rglob("*"))

    files_to_remove = all_files - files_to_keep
    files_to_remove = {f for f in files_to_remove if f.is_file()}

    with Path('/tmp/neurodocker-reprozip-trace/TO_DELETE.list').open('w') as f:
        print('\n'.join(map(str, sorted(files_to_remove))), file=f)

    # if not files_to_remove:
    #     print("No files to remove. Quitting.")
    #     return
    #
    # print("The following files will be removed:")
    # print('\n    ', end='')
    # print('\n    '.join(map(str, sorted(files_to_remove))))
    #
    # print(
    #     '\nWARNING: PROCEEDING MAY RESULT IN IRREVERSIBLE DATA LOSS, FOR EXAMPLE'
    #     ' IF ATTEMPTING TO REMOVE FILES IN DIRECTORIES MOUNTED FROM THE HOST.'
    #     ' PROCEED WITH EXTREME CAUTION! NEURODOCKER ASSUMES NO RESPONSIBILITY'
    #     ' FOR DATA LOSS. ALL OF THE FILES LISTED ABOVE WILL BE REMOVED.')
    # response = 'placeholder'
    # try:
    #     while response.lower() not in {'y', 'n', ''}:
    #         response = input('Proceed (y/N)? ')
    # except KeyboardInterrupt:
    #     print("Quitting.")
    #     return
    #
    # if response.lower() in {'', 'n'}:
    #     print("Quitting.")
    #     return
    #
    # msg = "\rRemoving files ({:.2f} %)"
    # n_files_to_remove = len(files_to_remove)
    # for i, f in enumerate(files_to_remove):
    #     f.unlink()
    #     print(msg.format((i+1)/n_files_to_remove*100), end='')
    # print()


if __name__ == '__main__':
    from argparse import ArgumentParser
    p = ArgumentParser(description=__doc__)
    p.add_argument("--config-file", required=True, help="`config.yml` file from `reprozip trace`.")
    p.add_argument("--dirs-to-prune", required=True, nargs='+', help="Directories to prune. Data will be lost in these directories.")
    args = p.parse_args()

    main(yaml_file=args.config_file, directories_to_prune=args.dirs_to_prune)
