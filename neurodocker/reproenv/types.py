"""Define types used in ReproEnv."""

import typing as ty

from mypy_extensions import TypedDict
from typing_extensions import Literal

allowed_installation_methods = {"binaries", "source"}
installation_methods_type = Literal["binaries", "source"]

allowed_pkg_managers = {"apt", "yum"}
pkg_managers_type = Literal["apt", "yum"]

# Cross-reference the dictionary types below with the JSON schemas.


class _InstallationDependenciesType(TypedDict, total=False):
    """Dictionary of system dependencies, with package managers as keys. Different
    distributions use different package managers. For example, CentOS and Fedora use
    `yum`, and Debian and Ubuntu use `apt` and `dpkg`.
    """

    apt: ty.List[str]
    debs: ty.List[str]
    yum: ty.List[str]


class _TemplateArgumentsType(TypedDict):
    """Arguments (i.e., variables) that are used in the template."""

    required: ty.List[str]
    optional: ty.Mapping[str, str]


class _BaseTemplateType(TypedDict, total=False):
    """Keys common to both types of templates: binaries and source."""

    arguments: _TemplateArgumentsType
    env: ty.Mapping[str, str]
    dependencies: _InstallationDependenciesType
    instructions: str


class _SourceTemplateType(_BaseTemplateType):
    """Template that defines how to install software by source."""

    pass


class _BinariesTemplateType(_BaseTemplateType):
    """Template that defines how to install software from pre-compiled binaries."""

    urls: ty.Mapping[str, str]


class TemplateType(TypedDict, total=False):
    """Dictionary that includes a template for installing software from binaries, a
    template for installing software from source, or both.
    """

    name: str
    binaries: _BinariesTemplateType
    source: _SourceTemplateType
    alert: str


class _SingularityHeaderType(TypedDict, total=False):
    """Dictionary that defines the header of a Singularity recipe."""

    bootstrap: str
    from_: str
