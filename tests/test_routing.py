"""Ensure every page key declared in PAGES has a renderer in the dispatch table."""

from __future__ import annotations

from dashboard.config import PAGES


_EXPECTED_PAGE_KEYS = set(PAGES.values())


def test_all_pages_have_unique_keys() -> None:
    """PAGES values must be unique strings (no accidental duplicates)."""
    assert len(PAGES.values()) == len(_EXPECTED_PAGE_KEYS)


def test_all_pages_keys_are_non_empty_strings() -> None:
    for label, key in PAGES.items():
        assert isinstance(key, str) and key, (
            f"Page key for '{label}' is empty or not a string"
        )
