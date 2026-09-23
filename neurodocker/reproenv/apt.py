"""Known APT package incompatibilities for official Debian image tags.

This is a diagnostic, not a package resolver or a complete support matrix.
"""

import re
from collections.abc import Iterable

# Debian package catalogs: https://packages.debian.org/<suite>/<package>
_UNAVAILABLE = {
    "buster": {"libtiff6", "openjdk-8-jre"},
    "bullseye": {"libtiff6", "multiarch-support", "openjdk-8-jre"},
    "bookworm": {"libtiff5", "multiarch-support", "openjdk-8-jre"},
    "trixie": {"libtiff5", "multiarch-support", "openjdk-8-jre", "libncurses5"},
}
_RELEASES = {"10": "buster", "11": "bullseye", "12": "bookworm", "13": "trixie"}


def unavailable_apt_packages(base_image: str, packages: Iterable[str]) -> list[str]:
    """Find known missing packages without inspecting or pulling a base image.

    Ignore custom repositories and floating tags, whose distributions cannot be
    inferred reliably from their names. Accept release, point-release, and slim tags.
    """
    image = base_image.split("@", 1)[0]
    match = re.fullmatch(
        r"(?:(?:docker\.io|index\.docker\.io)/)?(?:library/)?debian:"
        r"(?P<release>buster|bullseye|bookworm|trixie|1[0-3](?:\.\d+)?)"
        r"(?:-slim)?",
        image,
    )
    if match is None:
        return []
    release = match["release"].split(".", 1)[0]
    release = _RELEASES.get(release, release)
    return sorted(
        package
        for package in packages
        if package.split("=", 1)[0].split(":", 1)[0] in _UNAVAILABLE[release]
    )
