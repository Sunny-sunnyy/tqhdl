"""Rule-based insight templates. LLM client will be added in Phase 5."""

from __future__ import annotations

import pandas as pd

from data import compute_kpis


def _fmt_money(v: float) -> str:
    if v >= 1e9:
        return f"${v/1e9:.2f}B"
    if v >= 1e6:
        return f"${v/1e6:.1f}M"
    if v >= 1e3:
        return f"${v/1e3:.1f}K"
    return f"${v:,.0f}"


def _fmt_filters(filters: dict) -> str:
    parts = []
    for key, label in [
        ("year", "Year"),
        ("channel", "Channel"),
        ("us_region", "Region"),
        ("product_name", "Product"),
    ]:
        vals = filters.get(key) or []
        if vals:
            vals_str = ", ".join(map(str, vals[:3]))
            if len(vals) > 3:
                vals_str += f" (+{len(vals) - 3})"
            parts.append(f"**{label}**: {vals_str}")
    return " · ".join(parts) if parts else "Không có filter (toàn bộ dữ liệu)"


def overview_insight(df: pd.DataFrame, filters: dict) -> str:
    if df.empty:
        return "> **Không có dữ liệu** khớp với filter hiện tại. Hãy nới lỏng bộ lọc."

    k = compute_kpis(df)
    peak = (
        df.groupby(["order_month_num", "order_month_name"], as_index=False)["revenue"]
        .sum()
        .sort_values("revenue", ascending=False)
        .iloc[0]
    )

    return (
        f"### Key Findings — Executive Overview\n\n"
        f"*Scope: {_fmt_filters(filters)}*\n\n"
        f"- Tổng doanh thu **{_fmt_money(k['total_revenue'])}** qua **{k['total_orders']:,}** đơn hàng, "
        f"biên lợi nhuận trung bình **{k['profit_margin_pct']:.1f}%**.\n"
        f"- Tháng doanh thu cao nhất: **{peak['order_month_name']}** "
        f"(tổng {_fmt_money(peak['revenue'])}).\n"
        f"- Giá trị trung bình mỗi đơn: **{_fmt_money(k['revenue_per_order'])}**.\n"
    )


def product_channel_insight(df: pd.DataFrame, filters: dict) -> str:
    if df.empty:
        return "> Không có dữ liệu."

    top_product = df.groupby("product_name")["revenue"].sum().idxmax()
    top_product_rev = df.groupby("product_name")["revenue"].sum().max()

    ch_revenue = df.groupby("channel")["revenue"].sum().sort_values(ascending=False)
    top_channel = ch_revenue.index[0]
    top_channel_pct = ch_revenue.iloc[0] / ch_revenue.sum() * 100

    best_margin_ch = df.groupby("channel")["profit_margin_pct"].mean().sort_values(ascending=False)
    best_margin_ch_name = best_margin_ch.index[0]
    best_margin_val = best_margin_ch.iloc[0]

    return (
        f"### Key Findings — Product & Channel\n\n"
        f"*Scope: {_fmt_filters(filters)}*\n\n"
        f"- Sản phẩm top-seller: **{top_product}** ({_fmt_money(top_product_rev)}).\n"
        f"- Kênh chủ lực: **{top_channel}** chiếm **{top_channel_pct:.1f}%** doanh thu.\n"
        f"- Kênh có margin cao nhất: **{best_margin_ch_name}** "
        f"(trung bình **{best_margin_val:.1f}%**).\n"
    )
