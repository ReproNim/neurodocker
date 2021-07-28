"""Stateful objects in reproenv runtime."""

import copy
import json
import os
from pathlib import Path
import typing as ty

import jsonschema
import yaml

# The [C]SafeLoader will only load a subset of YAML, but that is fine for the
# purposes of this package.
try:
    from yaml import CSafeLoader as SafeLoader
except ImportError:  # pragma: no cover
    from yaml import SafeLoader  # type: ignore  # pragma: no cover

from neurodocker.reproenv.exceptions import RendererError
from neurodocker.reproenv.exceptions import TemplateError
from neurodocker.reproenv.exceptions import TemplateNotFound
from neurodocker.reproenv.types import TemplateType

_schemas_path = Path(__file__).parent / "schemas"

with (_schemas_path / "template.json").open("r") as f:
    _TEMPLATE_SCHEMA: ty.Dict = json.load(f)

with (_schemas_path / "renderer.json").open("r") as f:
    _RENDERER_SCHEMA: ty.Dict = json.load(f)


def _validate_template(template: TemplateType):
    """Validate template against JSON schema. Raise exception if invalid."""
    # TODO: should reproenv have a custom exception for invalid templates? probably
    try:
        jsonschema.validate(template, schema=_TEMPLATE_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise TemplateError(f"Invalid template: {e.message}.") from e

    # TODO: Check that all variables in the instructions are listed in arguments.
    # something like https://stackoverflow.com/a/8284419/5666087
    # but that solution does not get attributes like foo in `self.foo`.
    # For now, this is taken care of in Renderer classes, but it would be good to move
    # that behavior here, so we can catch errors early.
    pass


def _validate_renderer(d):
    """Validate renderer dictionary against JSON schema. Raise exception if invalid."""
    try:
        jsonschema.validate(d, schema=_RENDERER_SCHEMA)
    except jsonschema.exceptions.ValidationError as e:
        raise RendererError(f"Invalid renderer dictionary: {e.message}.") from e


class _TemplateRegistry:
    """Object to hold templates in memory."""

    _templates: ty.Dict[str, TemplateType] = {}

    @classmethod
    def _reset(cls):
        """Clear all templates."""
        cls._templates = {}

    @classmethod
    def register(
        cls,
        path_or_template: ty.Union[str, os.PathLike, TemplateType],
        name: str = None,
    ) -> TemplateType:
        """Register a template. This will overwrite an existing template with the
        same name in the registry.

        The template is validated against reproenv's template JSON schema upon
        registration. An invalid template will raise an exception.

        Parameters
        ----------
        path_or_template : str, Path-like, or TemplateType
            Path to YAML file that defines the template, or the dictionary that
            represents the template.
        name : str
            Name of the template. This becomes the key to the template in the registry.
            The name is made lower-case. If `path_or_template` is a path, then `name`
            can be omitted and instead comes from `template["name"]`. If
            `path_or_template` is a `dict`, then `name` is required.
        """
        if isinstance(path_or_template, dict):
            if name is None:
                raise ValueError("`name` required when template is not a file")
            name = str(name)
            template = copy.deepcopy(path_or_template)
        else:
            path_or_template = Path(path_or_template)
            if not path_or_template.is_file():
                raise ValueError("template is not path to a file or a dictionary")
            with path_or_template.open() as f:
                template = yaml.load(f, Loader=SafeLoader)

        _validate_template(template)
        if name is None:
            name = str(template["name"])

        # Add the template name as an optional key to the renderer schema. This is
        # so that the dictionary passed to the `Renderer.from_dict()` method can
        # contain names of registered templates. These templates are not known when the
        # renderer schema is created.
        # However, this schema is lax because the kwds just has to be an object. Keys
        # and values in kwds are validated in the renderer.
        key = f"template_{name.replace(' ', '_')}"
        _RENDERER_SCHEMA["definitions"][key] = {
            "required": ["name", "kwds"],
            "properties": {"name": {"enum": [name]}, "kwds": {"type": "object"}},
            "additionalProperties": False,
        }
        # Do not add template to `instructions` properties if it has already been added.
        template_ref = {"$ref": f"#/definitions/{key}"}
        oneof = _RENDERER_SCHEMA["properties"]["instructions"]["items"]["oneOf"]
        if template_ref not in oneof:
            oneof.append(template_ref)

        # Add template to registry.
        # TODO: should we log a message if overwriting a key-value pair?
        cls._templates[name.lower()] = template
        return template

    @classmethod
    def get(cls, name: str) -> TemplateType:
        """Return a Template object from the registry given a template name.

        Parameters
        ----------
        name : str
            The name of the registered template.

        If the template is not found, perhaps it was not added to the registry using
        `register`.
        """
        name = name.lower()
        try:
            return cls._templates[name]
        except KeyError:
            known = "', '".join(cls._templates.keys())
            raise TemplateNotFound(
                f"Unknown template '{name}'. Registered templates are '{known}'."
            )

    @classmethod
    def keys(cls) -> ty.KeysView[str]:
        """Return names of registered templates."""
        return cls._templates.keys()

    @classmethod
    def items(cls) -> ty.ItemsView[str, TemplateType]:
        return cls._templates.items()


register_template = _TemplateRegistry.register
registered_templates = _TemplateRegistry.keys
registered_templates_items = _TemplateRegistry.items
get_template = _TemplateRegistry.get
