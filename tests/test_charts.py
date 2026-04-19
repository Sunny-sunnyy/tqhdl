"""Smoke tests for Tab 1 chart builders."""

import plotly.graph_objects as go

from charts import (
    build_aov_histogram,
    build_kpi_cards_html,
    build_monthly_profit,
    build_monthly_revenue,
    build_price_margin_scatter,
)


def test_kpi_cards_returns_html_string(df_full):
    html = build_kpi_cards_html(df_full)
    assert isinstance(html, str)
    assert "kpi-card" in html
    assert "$" in html


def test_monthly_revenue_timeseries(df_full):
    fig = build_monthly_revenue(df_full, mode="timeseries")
    assert isinstance(fig, go.Figure)
    assert len(fig.data) >= 1


def test_monthly_revenue_seasonal(df_full):
    fig = build_monthly_revenue(df_full, mode="seasonal")
    assert isinstance(fig, go.Figure)


def test_monthly_profit(df_full):
    fig = build_monthly_profit(df_full)
    assert isinstance(fig, go.Figure)


def test_aov_histogram(df_full):
    fig = build_aov_histogram(df_full)
    assert isinstance(fig, go.Figure)


def test_price_margin_scatter(df_full):
    fig = build_price_margin_scatter(df_full)
    assert isinstance(fig, go.Figure)
