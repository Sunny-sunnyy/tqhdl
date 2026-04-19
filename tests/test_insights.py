"""Tests for rule-based insight functions and LLM integration."""

import os

import pandas as pd
import pytest

from insights import geo_customer_insight, llm_recommendation, overview_insight, product_channel_insight


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


def test_geo_customer_insight(df_full):
    text = geo_customer_insight(df_full, filters={})
    assert "California" in text or "CA" in text or "West" in text or "Midwest" in text


def test_summarize_for_llm_returns_dict(df_full):
    from data import summarize_for_llm
    s = summarize_for_llm(df_full, filters={"year": [2017]}, focus="overview")
    assert "kpis" in s
    assert "top_products" in s
    assert "filters" in s


@pytest.mark.skipif(not os.getenv("OPENAI_API_KEY"), reason="needs OPENAI_API_KEY")
def test_llm_recommendation_returns_markdown(df_full):
    text = llm_recommendation(df_full, filters={}, focus="overview")
    assert isinstance(text, str)
    assert len(text) > 50


def test_llm_recommendation_no_key_returns_error(df_full, monkeypatch):
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)
    text = llm_recommendation(df_full, filters={}, focus="overview")
    assert "Missing" in text or "⚠" in text
