"""Verify that the scripts package is importable (requires scripts/__init__.py)."""
from __future__ import annotations

import importlib


def test_scripts_package_importable() -> None:
    """scripts.__init__.py must exist for the dcca-build-analytics entry point to work."""
    mod = importlib.import_module('scripts.build_analytics_dataset')
    assert callable(getattr(mod, 'main', None))
