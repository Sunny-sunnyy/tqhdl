"""Pure chart builders. Each returns plotly.graph_objects.Figure (or HTML str for KPIs)."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

ACCENT = "#6b4eff"
ACCENT_SOFT = "#9b86ff"
MUTED = "#6b6b6b"
HEADER = "#3c3c40"

PLOTLY_LAYOUT = dict(
    template="plotly_white",
    margin=dict(l=40, r=20, t=40, b=40),
    font=dict(family="Inter, system-ui", size=12),
    title_font=dict(size=14, color=HEADER),
)


def _fmt_money(val: float) -> str:
    if val >= 1e9:
        return f"${val/1e9:.2f}B"
    if val >= 1e6:
        return f"${val/1e6:.1f}M"
    if val >= 1e3:
        return f"${val/1e3:.1f}K"
    return f"${val:,.0f}"


def _empty_figure(msg: str = "Khong co du lieu voi filter hien tai") -> go.Figure:
    fig = go.Figure()
    fig.add_annotation(
        text=msg, xref="paper", yref="paper", x=0.5, y=0.5,
        showarrow=False, font=dict(size=14, color=MUTED),
    )
    fig.update_layout(**PLOTLY_LAYOUT, xaxis=dict(visible=False), yaxis=dict(visible=False))
    return fig


def build_kpi_cards_html(df: pd.DataFrame) -> str:
    from data import compute_kpis

    k = compute_kpis(df)
    cards = [
        ("Total Revenue", _fmt_money(k["total_revenue"]), ""),
        ("Total Profit", _fmt_money(k["total_profit"]), ""),
        ("Profit Margin", f"{k['profit_margin_pct']:.1f}%", ""),
        ("Total Orders", f"{k['total_orders']:,}", ""),
        ("Revenue / Order", _fmt_money(k["revenue_per_order"]), ""),
    ]
    boxes = "".join(
        f"<div class='kpi-card'><div class='label'>{lbl}</div>"
        f"<div class='value'>{val}</div><div class='sub'>{sub}</div></div>"
        for lbl, val, sub in cards
    )
    return f"<div style='display:grid;grid-template-columns:repeat(5,1fr);gap:16px;'>{boxes}</div>"


def build_monthly_revenue(df: pd.DataFrame, mode: str = "timeseries") -> go.Figure:
    if df.empty:
        return _empty_figure()
    if mode == "timeseries":
        monthly = (
            df.groupby("order_month", as_index=False)["revenue"]
            .sum()
            .sort_values("order_month")
        )
        fig = px.line(monthly, x="order_month", y="revenue", markers=True, title="Monthly Revenue Trend")
        fig.update_traces(line_color=ACCENT, marker_color=ACCENT)
        fig.update_xaxes(title_text="Month")
    else:  # seasonal
        seasonal = (
            df.groupby(["order_month_num", "order_month_name"], as_index=False)["revenue"]
            .mean()
            .sort_values("order_month_num")
        )
        fig = px.bar(seasonal, x="order_month_name", y="revenue", title="Seasonal Revenue Pattern (avg across years)")
        fig.update_traces(marker_color=ACCENT)
        fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Revenue (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_monthly_profit(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    monthly = (
        df.groupby("order_month", as_index=False)["profit"]
        .sum()
        .sort_values("order_month")
    )
    fig = px.line(monthly, x="order_month", y="profit", markers=True, title="Monthly Profit Trend")
    fig.update_traces(line_color="#2e7d32", marker_color="#2e7d32")
    fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Profit (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_aov_histogram(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    order_values = df.groupby("order_number")["revenue"].sum()
    fig = px.histogram(order_values, nbins=50, title="Order Value Distribution")
    fig.update_traces(marker_color=ACCENT)
    fig.update_xaxes(title_text="Order Value (USD)")
    fig.update_yaxes(title_text="Number of Orders")
    fig.update_layout(showlegend=False, **PLOTLY_LAYOUT)
    return fig


def build_top_products_revenue(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty:
        return _empty_figure()
    top = df.groupby("product_name", as_index=False)["revenue"].sum().nlargest(n, "revenue")
    fig = px.bar(top, x="revenue", y="product_name", orientation="h", title=f"Top {n} Products by Revenue")
    fig.update_traces(marker_color=ACCENT)
    fig.update_yaxes(categoryorder="total ascending", title_text="")
    fig.update_xaxes(title_text="Revenue (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_top_products_profit(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty:
        return _empty_figure()
    top = df.groupby("product_name", as_index=False)["profit"].mean().nlargest(n, "profit")
    fig = px.bar(top, x="profit", y="product_name", orientation="h", title=f"Top {n} Products by Avg Profit")
    fig.update_traces(marker_color="#2e7d32")
    fig.update_yaxes(categoryorder="total ascending", title_text="")
    fig.update_xaxes(title_text="Avg Profit (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_channel_pie(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    by_ch = df.groupby("channel", as_index=False)["revenue"].sum()
    fig = px.pie(
        by_ch, names="channel", values="revenue", hole=0.4,
        title="Revenue Share by Channel",
        color_discrete_sequence=[ACCENT, ACCENT_SOFT, "#2e7d32"],
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_margin_by_channel(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    by_ch = (
        df.groupby("channel", as_index=False)["profit_margin_pct"]
        .mean()
        .sort_values("profit_margin_pct", ascending=False)
    )
    fig = px.bar(by_ch, x="channel", y="profit_margin_pct", title="Avg Profit Margin % by Channel", text="profit_margin_pct")
    fig.update_traces(marker_color=ACCENT, texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_yaxes(title_text="Margin %")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_price_boxplot(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    fig = px.box(df, x="product_name", y="unit_price", title="Unit Price Distribution per Product")
    fig.update_traces(marker_color=ACCENT)
    fig.update_xaxes(title_text="", tickangle=-45)
    fig.update_yaxes(title_text="Unit Price (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_price_margin_scatter(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    sample = df.sample(min(5000, len(df)), random_state=42) if len(df) > 5000 else df
    fig = px.scatter(
        sample, x="unit_price", y="profit_margin_pct",
        opacity=0.4, title="Profit Margin % vs Unit Price",
        hover_data=["product_name", "channel"],
    )
    fig.update_traces(marker_color=ACCENT)
    fig.update_xaxes(title_text="Unit Price (USD)")
    fig.update_yaxes(title_text="Profit Margin %")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_region_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    by_reg = (
        df.groupby("us_region", as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=True)
    )
    fig = px.bar(by_reg, x="revenue", y="us_region", orientation="h", title="Revenue by US Region")
    fig.update_traces(marker_color=ACCENT)
    fig.update_xaxes(title_text="Revenue (USD)")
    fig.update_yaxes(title_text="")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_state_choropleth(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    by_state = df.groupby("state", as_index=False)["revenue"].sum()
    fig = px.choropleth(
        by_state, locations="state", locationmode="USA-states",
        color="revenue", scope="usa",
        color_continuous_scale="Purples",
        title="Revenue by State",
    )
    fig.update_layout(**PLOTLY_LAYOUT, geo=dict(bgcolor="rgba(0,0,0,0)"))
    return fig


def build_states_dual_bar(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty:
        return _empty_figure()
    by_state = (
        df.groupby("state_name")
        .agg(revenue=("revenue", "sum"), orders=("order_number", "nunique"))
        .reset_index()
        .nlargest(n, "revenue")
        .sort_values("revenue")
    )
    fig = go.Figure()
    fig.add_trace(go.Bar(
        y=by_state["state_name"], x=by_state["revenue"],
        orientation="h", name="Revenue", marker_color=ACCENT,
    ))
    fig.add_trace(go.Bar(
        y=by_state["state_name"], x=by_state["orders"],
        orientation="h", name="Orders", marker_color=ACCENT_SOFT, xaxis="x2",
    ))
    fig.update_layout(
        title=f"Top {n} States — Revenue + Orders",
        xaxis=dict(title="Revenue (USD)", side="bottom"),
        xaxis2=dict(title="Orders", overlaying="x", side="top"),
        barmode="group",
        **PLOTLY_LAYOUT,
    )
    return fig


def build_customer_bar(df: pd.DataFrame, mode: str = "top", n: int = 10) -> go.Figure:
    if df.empty:
        return _empty_figure()
    grp = df.groupby("customer_name", as_index=False)["revenue"].sum()
    if mode == "top":
        selected = grp.nlargest(n, "revenue").sort_values("revenue")
        title = f"Top {n} Customers by Revenue"
        color = ACCENT
    else:
        selected = grp.nsmallest(n, "revenue").sort_values("revenue", ascending=False)
        title = f"Bottom {n} Customers by Revenue"
        color = "#ed6c02"
    fig = px.bar(selected, x="revenue", y="customer_name", orientation="h", title=title)
    fig.update_traces(marker_color=color)
    fig.update_yaxes(title_text="")
    fig.update_xaxes(title_text="Revenue (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_customer_bubble(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    seg = (
        df.groupby("customer_name")
        .agg(
            total_revenue=("revenue", "sum"),
            avg_margin=("profit_margin_pct", "mean"),
            n_orders=("order_number", "nunique"),
        )
        .reset_index()
    )
    fig = px.scatter(
        seg, x="total_revenue", y="avg_margin", size="n_orders",
        hover_name="customer_name", size_max=40,
        title="Customer Segmentation (Revenue x Margin x Orders)",
    )
    fig.update_traces(marker_color=ACCENT, marker_line=dict(color=HEADER, width=0.5))
    fig.update_xaxes(title_text="Total Revenue (USD)")
    fig.update_yaxes(title_text="Avg Profit Margin %")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    cols = ["quantity", "unit_price", "revenue", "cost", "profit"]
    corr = df[cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto",
        color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
        title="Correlation Heatmap",
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig
