from __future__ import annotations

import importlib


def test_build_analytics_entry_module_importable() -> None:
    """The analytics dataset build command module must be importable."""
    mod = importlib.import_module("dashboard.cli.build_analytics_dataset")
    assert mod is not None
    assert hasattr(mod, "main")
