"""Tests for rule-based insight functions."""

import pandas as pd

from insights import overview_insight, product_channel_insight


def test_overview_insight_returns_markdown_with_numbers(df_full):
    text = overview_insight(df_full, filters={})
    assert isinstance(text, str)
    assert "$" in text
    assert "%" in text
    assert len(text) > 100


def test_overview_insight_empty_df():
    empty = pd.DataFrame(
        columns=[
            "order_number", "revenue", "profit", "order_month_name",
            "order_month_num", "channel", "us_region", "product_name",
        ]
    )
    text = overview_insight(empty, filters={})
    assert "Không có dữ liệu" in text


def test_product_channel_insight(df_full):
    text = product_channel_insight(df_full, filters={})
    assert "Wholesale" in text or "Distributor" in text or "Export" in text
    assert "Product" in text
