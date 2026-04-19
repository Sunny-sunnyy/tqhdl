"""Tests for compute_kpis aggregation function."""

import pandas as pd
import pytest

from data import compute_kpis


def test_compute_kpis_returns_dict_with_expected_keys(df_full):
    kpis = compute_kpis(df_full)
    assert set(kpis.keys()) == {
        "total_revenue",
        "total_profit",
        "profit_margin_pct",
        "total_orders",
        "revenue_per_order",
    }


def test_compute_kpis_total_revenue_matches_sum(df_full):
    kpis = compute_kpis(df_full)
    assert abs(kpis["total_revenue"] - df_full["revenue"].sum()) < 1.0


def test_compute_kpis_total_orders_is_unique_count(df_full):
    kpis = compute_kpis(df_full)
    assert kpis["total_orders"] == df_full["order_number"].nunique()


def test_compute_kpis_empty_df_returns_zeros():
    empty = pd.DataFrame(columns=["revenue", "profit", "order_number"])
    kpis = compute_kpis(empty)
    assert kpis["total_revenue"] == 0
    assert kpis["total_orders"] == 0
