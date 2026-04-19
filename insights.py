"""Rule-based insight templates and OpenAI LLM recommendation client."""

from __future__ import annotations

import json
import os
from typing import Literal

import pandas as pd
from dotenv import load_dotenv

from data import compute_kpis, summarize_for_llm

load_dotenv()


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


def geo_customer_insight(df: pd.DataFrame, filters: dict) -> str:
    if df.empty:
        return "> Không có dữ liệu."

    region_rev = df.groupby("us_region")["revenue"].sum().sort_values(ascending=False)
    top_region = region_rev.index[0]
    top_region_pct = region_rev.iloc[0] / region_rev.sum() * 100

    state_rev = df.groupby("state_name")["revenue"].sum().sort_values(ascending=False)
    top_state = state_rev.index[0]

    cust_rev = df.groupby("customer_name")["revenue"].sum().sort_values(ascending=False)
    top_cust = cust_rev.index[0]
    top_cust_val = cust_rev.iloc[0]

    return (
        f"### Key Findings — Geography & Customer\n\n"
        f"*Scope: {_fmt_filters(filters)}*\n\n"
        f"- Vùng dẫn đầu: **{top_region}** ({top_region_pct:.1f}% doanh thu).\n"
        f"- Bang mạnh nhất: **{top_state}** ({_fmt_money(state_rev.iloc[0])}).\n"
        f"- Khách hàng top-spender: **{top_cust}** ({_fmt_money(top_cust_val)}).\n"
    )


_FOCUS_HINTS = {
    "overview": "Tập trung vào bức tranh tổng thể: doanh thu, lợi nhuận, xu hướng thời gian, đơn hàng.",
    "product_channel": "Tập trung vào hiệu suất sản phẩm và kênh phân phối, bao gồm margin và cấu trúc doanh thu.",
    "geo_customer": "Tập trung vào phân bố địa lý và phân khúc khách hàng: vùng, bang, top/bottom customer.",
}


def llm_recommendation(
    df: pd.DataFrame,
    filters: dict,
    focus: Literal["overview", "product_channel", "geo_customer"],
) -> str:
    """Call OpenAI and return a Markdown strategic recommendation."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "> **Missing OPENAI_API_KEY.** Tạo file `.env` từ `.env.example` "
            "và điền key của bạn để dùng tính năng này."
        )

    summary = summarize_for_llm(df, filters, focus)

    try:
        from openai import OpenAI

        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        system = (
            "Bạn là senior sales data analyst. Hãy đưa 3-5 khuyến nghị chiến lược "
            "ngắn gọn, hành động được, dựa trên số liệu thật trong data summary. "
            "Mỗi bullet dưới 2 câu, tiếng Việt, có kèm số liệu cụ thể (dollar, %, tên "
            "sản phẩm/vùng/kênh). Không bịa thông tin ngoài data summary."
        )
        user = (
            f"Trọng tâm phân tích: **{focus}**.\n"
            f"Gợi ý: {_FOCUS_HINTS[focus]}\n\n"
            f"Data summary (JSON):\n```json\n{json.dumps(summary, ensure_ascii=False, indent=2)}\n```\n\n"
            f"Trả về Markdown với heading '### Strategic Recommendations' và danh sách bullet."
        )

        resp = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.4,
            max_tokens=600,
            timeout=15,
        )
        return resp.choices[0].message.content or "(empty response)"
    except Exception as e:
        return f"> **LLM call failed:** `{type(e).__name__}: {e}`"
