"""Keep template registration local to each test."""

from copy import deepcopy

import pytest

from neurodocker.reproenv import state


@pytest.fixture(autouse=True)
def isolate_template_registry(monkeypatch):
    monkeypatch.setattr(
        state._TemplateRegistry,
        "_templates",
        deepcopy(state._TemplateRegistry._templates),
    )
    monkeypatch.setattr(state, "_RENDERER_SCHEMA", deepcopy(state._RENDERER_SCHEMA))
