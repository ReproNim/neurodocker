"""Remove all files under a directory but not caught by `reprozip trace`."""

from pathlib import Path
import typing as ty

import yaml

# TODO: if removing all of the files in a directory, print that directory with a *.
# pip does this in `pip uninstall`.


def _in_docker() -> bool:
    if not Path("/proc/1/cgroup").is_file():
        return False
    # TODO: this is not a long-term solution.
    return Path("/.dockerenv").is_file()


def main(
    *,
    yaml_file: ty.Union[str, Path],
    directories_to_prune: ty.Union[ty.List[str], ty.List[Path]],
):

    if not _in_docker():
        raise RuntimeError(
            "Not running in a Docker container. This script should only be used within"
            " a container."
        )

    yaml_file = Path(yaml_file)
    if yaml_file.name != "config.yml":
        raise ValueError("File should be named `config.yml`")
    with yaml_file.open(mode="r") as f:
        config = yaml.load(f, Loader=yaml.SafeLoader)

    # Paths caught by `reprozip trace`. These can be directories or files.
    # There could potentially be other information (e.g., input/output,
    # packages), but we are only interested in the contents of this key.
    files_to_keep = config["other_files"]
    files_to_keep = {Path(p) for p in files_to_keep}

    if isinstance(directories_to_prune, (Path, str)):
        directories_to_prune = [directories_to_prune]

    directories_to_prune = [Path(d) for d in directories_to_prune]

    # TODO: consider moving this check to the `neurodocker minify` cli. perhaps make a
    # new click paramtype that checks if the directory exists in the container.
    for d in directories_to_prune:
        if not d.is_dir():
            raise ValueError(f"Directory does not exist: {d}")

    all_files: ty.Set[Path] = set()
    for d in directories_to_prune:
        all_files.update(Path(d).rglob("*"))

    files_to_remove = all_files - files_to_keep
    files_to_remove = {f for f in files_to_remove if f.is_file()}

    with open(
        "/tmp/neurodocker-reprozip-trace/TO_DELETE.list", mode="w", encoding="utf-8"
    ) as f:
        n_errored = 0
        for ff in sorted(files_to_remove):
            try:
                print(ff, file=f)
            except UnicodeEncodeError:
                n_errored += 1

    print(f"++ skipping {n_errored} files due to unicode encoding errors")
    print(f"++ found {len(files_to_remove) - n_errored} files to remove")


if __name__ == "__main__":
    from argparse import ArgumentParser

    p = ArgumentParser(description=__doc__)
    p.add_argument(
        "--config-file", required=True, help="`config.yml` file from `reprozip trace`."
    )
    p.add_argument(
        "--dirs-to-prune",
        required=True,
        nargs="+",
        help="Directories to prune. Data will be lost in these directories.",
    )
    args = p.parse_args()

    main(yaml_file=args.config_file, directories_to_prune=args.dirs_to_prune)
