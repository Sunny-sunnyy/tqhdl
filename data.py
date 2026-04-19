"""Data loading and filtering for the Regional Sales dashboard."""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

import pandas as pd

CSV_PATH = Path(__file__).parent / "Sales_data(EDA Exported).csv"

REQUIRED_COLUMNS: frozenset[str] = frozenset(
    {
        "order_number",
        "order_date",
        "customer_name",
        "channel",
        "product_name",
        "quantity",
        "unit_price",
        "revenue",
        "cost",
        "state",
        "state_name",
        "us_region",
        "profit",
        "profit_margin_pct",
        "order_month_name",
        "order_month_num",
        "order_month",
    }
)

FilterDict = dict[str, list[Any]]


def load_csv(path: Path = CSV_PATH) -> pd.DataFrame:
    """Load the exported EDA CSV and parse order_date as datetime."""
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {sorted(missing)}")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def apply_filters(df: pd.DataFrame, filters: FilterDict) -> pd.DataFrame:
    """Apply a filter dict to df.

    Empty list / missing key for a dimension means no filtering on it.
    Supported keys: year, channel, us_region, product_name.
    """
    mask = pd.Series(True, index=df.index)

    if years := filters.get("year"):
        mask &= df["order_date"].dt.year.isin(years)
    if channels := filters.get("channel"):
        mask &= df["channel"].isin(channels)
    if regions := filters.get("us_region"):
        mask &= df["us_region"].isin(regions)
    if products := filters.get("product_name"):
        mask &= df["product_name"].isin(products)

    return df.loc[mask].copy()


def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    """Return aggregate KPIs for the given (possibly filtered) DataFrame."""
    if df.empty:
        return {
            "total_revenue": 0.0,
            "total_profit": 0.0,
            "profit_margin_pct": 0.0,
            "total_orders": 0,
            "revenue_per_order": 0.0,
        }
    total_revenue = float(df["revenue"].sum())
    total_profit = float(df["profit"].sum())
    total_orders = int(df["order_number"].nunique())
    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "profit_margin_pct": (total_profit / total_revenue * 100) if total_revenue else 0.0,
        "total_orders": total_orders,
        "revenue_per_order": total_revenue / total_orders if total_orders else 0.0,
    }


def summarize_for_llm(
    df: pd.DataFrame,
    filters: dict,
    focus: Literal["overview", "product_channel", "geo_customer"],
) -> dict:
    """Build a compact JSON-serializable summary to send to the LLM."""
    if df.empty:
        return {"filters": filters, "focus": focus, "empty": True}

    k = compute_kpis(df)
    top_products = (
        df.groupby("product_name")["revenue"].sum()
        .nlargest(5).reset_index().to_dict("records")
    )
    top_channels = (
        df.groupby("channel")["revenue"].sum()
        .sort_values(ascending=False).reset_index().to_dict("records")
    )
    top_regions = (
        df.groupby("us_region")["revenue"].sum()
        .sort_values(ascending=False).reset_index().to_dict("records")
    )
    top_states = (
        df.groupby("state_name")["revenue"].sum()
        .nlargest(5).reset_index().to_dict("records")
    )
    peak_month_idx = (
        df.groupby(["order_month_num", "order_month_name"])["revenue"].sum().idxmax()
    )
    return {
        "filters": filters,
        "focus": focus,
        "kpis": {k_: round(v, 2) if isinstance(v, float) else v for k_, v in k.items()},
        "top_products": top_products,
        "top_channels": top_channels,
        "top_regions": top_regions,
        "top_states": top_states,
        "peak_month": peak_month_idx[1],
    }
