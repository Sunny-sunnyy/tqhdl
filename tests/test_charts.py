"""Smoke tests for chart builders (Tab 1 + Tab 2 + Tab 3)."""

import plotly.graph_objects as go

from charts import (
    build_aov_histogram,
    build_channel_pie,
    build_correlation_heatmap,
    build_customer_bar,
    build_customer_bubble,
    build_kpi_cards_html,
    build_margin_by_channel,
    build_monthly_profit,
    build_monthly_revenue,
    build_price_boxplot,
    build_region_bar,
    build_revenue_profit_by_channel,
    build_state_choropleth,
    build_states_dual_bar,
    build_top_products_profit,
    build_top_products_revenue,
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


def test_revenue_profit_by_channel(df_full):
    fig = build_revenue_profit_by_channel(df_full)
    assert isinstance(fig, go.Figure)
    assert len(fig.data) == 2  # two bar groups: revenue + profit


# --- Tab 2 ---

def test_top_products_revenue(df_full):
    assert isinstance(build_top_products_revenue(df_full), go.Figure)


def test_top_products_profit(df_full):
    assert isinstance(build_top_products_profit(df_full), go.Figure)


def test_channel_pie(df_full):
    assert isinstance(build_channel_pie(df_full), go.Figure)


def test_margin_by_channel(df_full):
    assert isinstance(build_margin_by_channel(df_full), go.Figure)


def test_price_boxplot(df_full):
    assert isinstance(build_price_boxplot(df_full), go.Figure)


# --- Tab 3 ---

def test_region_bar(df_full):
    assert isinstance(build_region_bar(df_full), go.Figure)


def test_state_choropleth(df_full):
    assert isinstance(build_state_choropleth(df_full), go.Figure)


def test_states_dual_bar(df_full):
    assert isinstance(build_states_dual_bar(df_full), go.Figure)


def test_customer_bar_top(df_full):
    assert isinstance(build_customer_bar(df_full, mode="top"), go.Figure)


def test_customer_bar_bottom(df_full):
    assert isinstance(build_customer_bar(df_full, mode="bottom"), go.Figure)


def test_customer_bubble(df_full):
    assert isinstance(build_customer_bubble(df_full), go.Figure)


def test_correlation_heatmap(df_full):
    assert isinstance(build_correlation_heatmap(df_full), go.Figure)
