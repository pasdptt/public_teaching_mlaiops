"""Data tests.

Two kinds live here, and Lab 4 asks you to tell them apart:

  * schema / contract tests — assertions about the DATA. They fail when an upstream
    producer changes something, even though your code is untouched.
  * property tests — assertions about your splitting LOGIC. They fail when you change
    the code.

test_no_machine_leaks_across_splits is the one that matters most. It is the single
most common silent error in student projects: readings from one machine appearing in
both train and validation, producing a score that never survives contact with
production.
"""
from __future__ import annotations

import pytest

from src import config, data

RAW = config.REPO_ROOT / "data" / "raw" / "sensors.csv"


@pytest.fixture(scope="module")
def df():
    if not RAW.exists():
        pytest.skip("data/raw/sensors.csv missing — run `make data` or `dvc pull` first")
    return data.load_raw(RAW)


# --- contract tests: about the data -------------------------------------------------

def test_schema_columns_present_and_typed(df):
    missing = set(data.SCHEMA) - set(df.columns)
    assert not missing, f"missing columns: {sorted(missing)}"
    unexpected = set(df.columns) - set(data.SCHEMA)
    assert not unexpected, f"unexpected columns: {sorted(unexpected)}"
    for col, expected in data.SCHEMA.items():
        assert str(df[col].dtype) == expected, f"{col}: expected {expected}, got {df[col].dtype}"


def test_no_nulls_in_required_columns(df):
    nulls = df[list(data.SCHEMA)].isna().sum()
    offenders = nulls[nulls > 0]
    assert offenders.empty, f"null values found: {offenders.to_dict()}"


def test_features_within_plausible_ranges(df):
    for col, (lo, hi) in data.PLAUSIBLE_RANGES.items():
        assert df[col].min() >= lo, f"{col} below plausible floor: {df[col].min()}"
        assert df[col].max() <= hi, f"{col} above plausible ceiling: {df[col].max()}"


def test_target_is_binary_and_not_degenerate(df):
    values = set(df[data.TARGET].unique().tolist())
    assert values <= {0, 1}, f"target has values outside 0/1: {values}"
    rate = df[data.TARGET].mean()
    assert 0.01 < rate < 0.99, f"target is degenerate, positive rate = {rate:.4f}"


def test_identifier_is_unique(df):
    assert df[data.ID].is_unique, "reading_id is not unique"


# --- property tests: about the splitting logic --------------------------------------

def test_no_machine_leaks_across_splits(df):
    train, val, test = data.split(df, seed=42)
    tr, va, te = (set(p[data.GROUP]) for p in (train, val, test))
    assert not tr & va, f"machines in both train and val: {sorted(tr & va)[:5]}"
    assert not tr & te, f"machines in both train and test: {sorted(tr & te)[:5]}"
    assert not va & te, f"machines in both val and test: {sorted(va & te)[:5]}"


def test_split_is_deterministic_given_seed(df):
    a = data.split(df, seed=7)
    b = data.split(df, seed=7)
    for pa, pb in zip(a, b):
        assert pa[data.ID].tolist() == pb[data.ID].tolist()


def test_split_changes_with_seed(df):
    a, _, _ = data.split(df, seed=1)
    b, _, _ = data.split(df, seed=2)
    assert a[data.ID].tolist() != b[data.ID].tolist(), "seed has no effect — split is not random"


def test_every_row_lands_in_exactly_one_split(df):
    train, val, test = data.split(df, seed=13)
    total = len(train) + len(val) + len(test)
    assert total == len(df), f"rows lost or duplicated: {total} vs {len(df)}"


def test_data_fingerprint_is_stable():
    if not RAW.exists():
        pytest.skip("no raw data")
    assert data.data_fingerprint(RAW) == data.data_fingerprint(RAW)
