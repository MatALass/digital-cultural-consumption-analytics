from __future__ import annotations

import math

import numpy as np
import pandas as pd
import pytest

from dcca.stats import (
    MIN_BASE,
    bootstrap_median,
    independence_test,
    share,
    share_table,
    wilson_interval,
)


def test_wilson_matches_reference_value():
    # Valeur de référence : 50 succès sur 100 -> [0,4038 ; 0,5962]
    low, high = wilson_interval(50, 100)
    assert low == pytest.approx(0.4038, abs=1e-4)
    assert high == pytest.approx(0.5962, abs=1e-4)


@pytest.mark.parametrize("k,n", [(0, 10), (10, 10), (1, 1), (0, 1)])
def test_wilson_stays_in_unit_interval_at_the_edges(k, n):
    low, high = wilson_interval(k, n)
    assert 0.0 <= low <= k / n <= high <= 1.0


def test_wilson_on_empty_base_returns_nan():
    low, high = wilson_interval(0, 0)
    assert math.isnan(low) and math.isnan(high)


def test_wilson_rejects_impossible_counts():
    with pytest.raises(ValueError):
        wilson_interval(11, 10)


def test_share_ignores_missing_values():
    s = share(pd.Series([True, False, None, True], dtype="boolean"))
    assert (s.successes, s.base) == (2, 3)
    assert s.value == pytest.approx(2 / 3)


def test_share_flags_small_bases_as_unreliable():
    small = share(pd.Series([True] * (MIN_BASE - 1)))
    large = share(pd.Series([True] * MIN_BASE))
    assert not small.reliable
    assert large.reliable


def test_share_table_keeps_requested_order_and_bases():
    df = pd.DataFrame({"groupe": ["b", "a", "b", "c"], "flag": [True, False, False, True]})
    out = share_table(df, "flag", "groupe", order=["c", "b", "a"])
    assert list(out["groupe"]) == ["c", "b", "a"]
    assert list(out["base"]) == [1, 2, 1]
    assert out.loc[out["groupe"] == "b", "part"].item() == pytest.approx(0.5)


def test_share_table_on_empty_frame_has_expected_columns():
    out = share_table(pd.DataFrame({"g": [], "f": []}), "f", "g")
    assert out.empty
    assert {"part", "ic_bas", "ic_haut", "base", "fiable"} <= set(out.columns)


def test_bootstrap_median_is_reproducible_and_brackets_the_median():
    values = pd.Series(np.arange(1, 101, dtype=float))
    first = bootstrap_median(values, n_boot=500, seed=1)
    second = bootstrap_median(values, n_boot=500, seed=1)
    assert first == second
    median, low, high = first
    assert median == 50.5
    assert low <= median <= high


def test_bootstrap_median_on_empty_series_returns_nan():
    assert all(math.isnan(x) for x in bootstrap_median(pd.Series([], dtype=float)))


def test_independence_test_detects_a_strong_link():
    df = pd.DataFrame({"x": ["a"] * 50 + ["b"] * 50, "y": ["u"] * 50 + ["v"] * 50})
    result = independence_test(df, "x", "y")
    assert result.p_value < 1e-10
    assert result.cramers_v == pytest.approx(1.0, abs=0.05)


def test_independence_test_on_independent_variables():
    df = pd.DataFrame({"x": ["a", "a", "b", "b"] * 50, "y": ["u", "v", "u", "v"] * 50})
    result = independence_test(df, "x", "y")
    assert result.cramers_v == pytest.approx(0.0, abs=1e-9)
    assert result.p_value > 0.9


def test_independence_test_with_a_single_level_returns_nan():
    df = pd.DataFrame({"x": ["a"] * 10, "y": ["u", "v"] * 5})
    assert math.isnan(independence_test(df, "x", "y").p_value)
