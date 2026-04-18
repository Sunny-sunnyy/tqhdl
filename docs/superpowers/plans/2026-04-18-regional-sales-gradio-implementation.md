# Regional Sales Gradio Dashboard — Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Xây một Gradio web app 4 tab (Overview / Product & Channel / Geography & Customer / Explorer) tái hiện và mở rộng Power BI dashboard của dự án USA Regional Sales 2014–2018, với global filter bar, chart Plotly tương tác, PyGWalker cho Explorer, rule-based insights + nút LLM (OpenAI) sinh strategic recommendation.

**Architecture:** Gradio `Blocks` với shared `gr.State` (df_full, df_filtered, filter_dict). Filter change event recompute `df_filtered` một lần, trigger tất cả chart callback đồng loạt re-render. Chart builders là pure function trong `charts.py`, rule insights trong `insights.py`, load + filter trong `data.py`, CSS trong `theme.py`. LLM gọi OpenAI `gpt-4o-mini` on-demand qua button.

**Tech Stack:** Python 3.11, uv, pandas, plotly, gradio, pygwalker, openai, python-dotenv, pytest (dev), matplotlib/seaborn (tham khảo notebook gốc, không dùng trong app).

**Reference docs (đọc trước khi làm):**
- Spec: `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md`
- Handoff: `HANDOFF.md`
- Codebase guide: `CLAUDE.md`

---

## File Structure

| File | Responsibility | Created in |
|---|---|---|
| `data.py` | Load CSV một lần, apply global filters, summarize dataframe cho LLM prompt | Phase 1 |
| `charts.py` | 16 chart builder function (pure, nhận df, trả `plotly.graph_objects.Figure`) | Phase 2–4 |
| `insights.py` | Rule-based insight template mỗi tab + OpenAI client wrapper + prompt builder | Phase 2–5 |
| `theme.py` | Custom CSS string, color palette constants | Phase 1 |
| `app.py` | Gradio `Blocks` UI: filter bar, 4 tab, event handler, state management | Phase 1 (skeleton), Phase 2–6 (fill) |
| `tests/test_data.py` | Unit test `apply_filters`, `load_csv` | Phase 1 |
| `tests/test_charts.py` | Smoke test chart builder trả về Figure hợp lệ | Phase 2–4 |
| `tests/test_insights.py` | Rule template format + LLM client error handling | Phase 2, 5 |
| `tests/conftest.py` | pytest fixture `sample_df` | Phase 1 |
| `.env.example` | Template API key | (đã tạo) |
| `.gitignore` | Loại trừ `.env`, `.venv`, cache | (đã tạo) |
| `README.md` | Hướng dẫn chạy, screenshot, deps | Phase 7 |

**Invariants:**
- `data.py`, `charts.py`, `insights.py` **không import Gradio**. Chỉ `app.py` import Gradio. Giúp test dễ, tách UI khỏi logic.
- Chart builders là **pure functions**: cùng input → cùng output. Không side effect.
- Filter semantic: rỗng list = không lọc (giữ tất cả). Áp dụng nhất quán ở `apply_filters`.

---

## Phases Overview

| Phase | Tasks | Est. | Demo-able after? |
|---|---|---|---|
| 1. Foundation | 1–5 | 3h | ✓ app chạy, filter bar có action, tab rỗng |
| 2. Tab 1 Overview | 6–10 | 4h | ✓ Tab 1 đầy đủ 5 KPI + 4 chart + insight |
| 3. Tab 2 Product & Channel | 11–14 | 3h | ✓ |
| 4. Tab 3 Geo & Customer | 15–19 | 5h | ✓ |
| 5. LLM integration | 20–22 | 2h | ✓ full demo |
| 6. Tab 4 Explorer | 23–24 | 2h | ✓ |
| 7. Polish & docs | 25–28 | 3h | ✓ ready to submit |
| 8. Phase 2 stretch (upload) | 29–30 | — | — |

---

## Phase 1: Foundation

### Task 1: Add dependencies

**Files:** Modify `pyproject.toml`

- [ ] **Step 1: Add runtime + dev deps via uv**

```bash
uv add gradio pygwalker openai python-dotenv
uv add --dev pytest
```

- [ ] **Step 2: Verify**

```bash
uv run python -c "import gradio, pygwalker, openai, dotenv; print(gradio.__version__, openai.__version__)"
```
Expected: version numbers print, không lỗi import.

- [ ] **Step 3: Commit**

```bash
git add pyproject.toml uv.lock
git commit -m "chore: add gradio, pygwalker, openai, dotenv, pytest deps"
```

---

### Task 2: `data.py` — load + validate schema + apply_filters (TDD)

**Files:**
- Create: `data.py`
- Create: `tests/__init__.py` (empty file)
- Create: `tests/conftest.py`
- Create: `tests/test_data.py`

- [ ] **Step 1: Create `tests/conftest.py` with shared fixture**

```python
# tests/conftest.py
from pathlib import Path
import pandas as pd
import pytest

CSV_PATH = Path(__file__).parent.parent / "Sales_data(EDA Exported).csv"


@pytest.fixture(scope="session")
def df_full() -> pd.DataFrame:
    df = pd.read_csv(CSV_PATH)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


@pytest.fixture
def sample_df(df_full) -> pd.DataFrame:
    return df_full.head(100).copy()
```

- [ ] **Step 2: Write failing test for `load_csv`**

```python
# tests/test_data.py
import pandas as pd
from data import load_csv, apply_filters


def test_load_csv_returns_dataframe_with_expected_columns():
    df = load_csv()
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 64104
    required = {
        "order_number", "order_date", "customer_name", "channel",
        "product_name", "quantity", "unit_price", "revenue", "cost",
        "state", "state_name", "us_region", "profit", "profit_margin_pct",
        "order_month_name", "order_month_num", "order_month",
    }
    assert required.issubset(df.columns)


def test_load_csv_parses_order_date_as_datetime():
    df = load_csv()
    assert pd.api.types.is_datetime64_any_dtype(df["order_date"])
```

- [ ] **Step 3: Run tests — should fail (module not yet created)**

```bash
uv run pytest tests/test_data.py -v
```
Expected: `ModuleNotFoundError: No module named 'data'`

- [ ] **Step 4: Create `data.py` with minimal `load_csv`**

```python
# data.py
"""Data loading and filtering for Regional Sales dashboard."""
from pathlib import Path
import pandas as pd

CSV_PATH = Path(__file__).parent / "Sales_data(EDA Exported).csv"

REQUIRED_COLUMNS = {
    "order_number", "order_date", "customer_name", "channel",
    "product_name", "quantity", "unit_price", "revenue", "cost",
    "state", "state_name", "us_region", "profit", "profit_margin_pct",
    "order_month_name", "order_month_num", "order_month",
}


def load_csv(path: Path = CSV_PATH) -> pd.DataFrame:
    df = pd.read_csv(path)
    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise ValueError(f"CSV missing columns: {missing}")
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df
```

- [ ] **Step 5: Run tests — should pass**

```bash
uv run pytest tests/test_data.py::test_load_csv_returns_dataframe_with_expected_columns tests/test_data.py::test_load_csv_parses_order_date_as_datetime -v
```
Expected: 2 passed.

- [ ] **Step 6: Write failing tests for `apply_filters`**

```python
# append to tests/test_data.py

def test_apply_filters_empty_returns_all(df_full):
    filtered = apply_filters(df_full, {})
    assert len(filtered) == len(df_full)


def test_apply_filters_year(df_full):
    filtered = apply_filters(df_full, {"year": [2017]})
    assert filtered["order_date"].dt.year.unique().tolist() == [2017]


def test_apply_filters_channel(df_full):
    filtered = apply_filters(df_full, {"channel": ["Wholesale"]})
    assert filtered["channel"].unique().tolist() == ["Wholesale"]


def test_apply_filters_region(df_full):
    filtered = apply_filters(df_full, {"us_region": ["West"]})
    assert filtered["us_region"].unique().tolist() == ["West"]


def test_apply_filters_product_multiselect(df_full):
    filtered = apply_filters(df_full, {"product_name": ["Product 26", "Product 27"]})
    assert set(filtered["product_name"].unique()) == {"Product 26", "Product 27"}


def test_apply_filters_combined(df_full):
    filtered = apply_filters(df_full, {
        "year": [2017],
        "channel": ["Export"],
        "us_region": ["West"],
    })
    assert filtered["order_date"].dt.year.unique().tolist() == [2017]
    assert filtered["channel"].unique().tolist() == ["Export"]
    assert filtered["us_region"].unique().tolist() == ["West"]


def test_apply_filters_empty_list_means_no_filter(df_full):
    filtered = apply_filters(df_full, {"channel": []})
    assert set(filtered["channel"].unique()) == set(df_full["channel"].unique())
```

- [ ] **Step 7: Run tests — should fail (function not defined)**

```bash
uv run pytest tests/test_data.py -v
```
Expected: AttributeError or ImportError for `apply_filters`.

- [ ] **Step 8: Implement `apply_filters`**

Add to `data.py`:

```python
from typing import Any

FilterDict = dict[str, list[Any]]


def apply_filters(df: pd.DataFrame, filters: FilterDict) -> pd.DataFrame:
    """Apply filter dict to df. Empty list/None for a key means no filter on that dim."""
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
```

- [ ] **Step 9: Run all tests**

```bash
uv run pytest tests/test_data.py -v
```
Expected: all 9 tests pass.

- [ ] **Step 10: Commit**

```bash
git add data.py tests/
git commit -m "feat(data): load_csv with schema validation + apply_filters"
```

---

### Task 3: `theme.py` — CSS + color palette

**Files:** Create `theme.py`

- [ ] **Step 1: Create `theme.py`**

```python
# theme.py
"""Custom CSS + palette để match Canva background của dự án gốc."""

COLORS = {
    "header_bg": "#3c3c40",
    "page_bg": "#f6f6f6",
    "card_bg": "#ffffff",
    "accent": "#6b4eff",
    "accent_soft": "#9b86ff",
    "text_primary": "#1a1a1a",
    "text_muted": "#6b6b6b",
    "success": "#2e7d32",
    "warning": "#ed6c02",
}

CUSTOM_CSS = """
/* Reset padding */
.gradio-container {background: #f6f6f6 !important; font-family: Inter, system-ui, sans-serif;}

/* Header */
#app-header {
    background: #3c3c40; color: white; padding: 20px 32px;
    border-radius: 0; margin: -16px -16px 16px -16px;
}
#app-header h1 {margin: 0; font-size: 24px; font-weight: 600;}
#app-header .subtitle {color: #c9c6d9; font-size: 13px; margin-top: 4px;}

/* Filter bar */
#filter-bar {
    background: white; border-radius: 12px; padding: 16px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08); margin-bottom: 16px;
}
#filter-bar label {font-weight: 600; color: #3c3c40;}

/* KPI cards */
.kpi-card {
    background: white; border-radius: 16px; padding: 20px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.10);
    border-top: 3px solid #6b4eff; min-height: 110px;
}
.kpi-card .label {color: #6b6b6b; font-size: 13px; text-transform: uppercase; letter-spacing: 0.5px;}
.kpi-card .value {font-size: 28px; font-weight: 700; color: #1a1a1a; margin-top: 8px;}
.kpi-card .sub {color: #6b6b6b; font-size: 12px; margin-top: 4px;}

/* Chart panel */
.chart-panel {
    background: white; border-radius: 12px; padding: 8px;
    box-shadow: 0 2px 6px rgba(0,0,0,0.08);
}

/* Insight panel */
.insight-panel {
    background: #f3f1ff; border-left: 4px solid #6b4eff;
    border-radius: 8px; padding: 16px; margin: 8px 0;
}
.insight-panel h4 {margin-top: 0; color: #3c3c40;}

/* LLM output */
.llm-output {
    background: #fff7e6; border-left: 4px solid #ed6c02;
    border-radius: 8px; padding: 16px;
}

/* Tab styling */
.tabs button.selected {color: #6b4eff !important; border-color: #6b4eff !important;}
"""
```

- [ ] **Step 2: Smoke check — CSS string parseable**

```bash
uv run python -c "from theme import CUSTOM_CSS, COLORS; assert len(CUSTOM_CSS) > 500 and COLORS['accent'] == '#6b4eff'; print('ok')"
```
Expected: `ok`.

- [ ] **Step 3: Commit**

```bash
git add theme.py
git commit -m "feat(theme): custom CSS + color palette"
```

---

### Task 4: `app.py` skeleton — filter bar + 4 empty tabs

**Files:** Create `app.py`

- [ ] **Step 1: Create `app.py` skeleton**

```python
# app.py
"""Regional Sales Gradio Dashboard — entry point."""
from __future__ import annotations

import gradio as gr
import pandas as pd

from data import load_csv, apply_filters
from theme import CUSTOM_CSS


def build_filter_state(
    df_full: pd.DataFrame,
    years: list[int],
    channels: list[str],
    regions: list[str],
    products: list[str],
) -> tuple[pd.DataFrame, dict]:
    filters = {
        "year": years or [],
        "channel": channels or [],
        "us_region": regions or [],
        "product_name": products or [],
    }
    df_filtered = apply_filters(df_full, filters)
    return df_filtered, filters


def clear_filters() -> tuple[list, list, list, list]:
    return [], [], [], []


def build_app() -> gr.Blocks:
    df_full = load_csv()
    year_choices = sorted(df_full["order_date"].dt.year.unique().tolist())
    channel_choices = sorted(df_full["channel"].unique().tolist())
    region_choices = sorted(df_full["us_region"].unique().tolist())
    product_choices = sorted(df_full["product_name"].unique().tolist())

    with gr.Blocks(
        theme=gr.themes.Soft(),
        css=CUSTOM_CSS,
        title="USA Regional Sales Dashboard",
    ) as app:
        df_full_state = gr.State(df_full)
        df_filtered_state = gr.State(df_full)
        filter_dict_state = gr.State({})

        gr.HTML(
            """
            <div id='app-header'>
                <h1>USA Regional Sales Dashboard</h1>
                <div class='subtitle'>Acme Co. · 2014–2018 · Trực quan hoá dữ liệu bán hàng</div>
            </div>
            """
        )

        with gr.Row(elem_id="filter-bar"):
            year_f = gr.CheckboxGroup(year_choices, label="Year", value=year_choices)
            channel_f = gr.CheckboxGroup(channel_choices, label="Channel", value=channel_choices)
            region_f = gr.CheckboxGroup(region_choices, label="US Region", value=region_choices)
            product_f = gr.Dropdown(product_choices, label="Product", multiselect=True, value=[])
            clear_btn = gr.Button("Clear Filters", variant="secondary", scale=0)

        with gr.Tabs() as tabs:
            with gr.Tab("Overview"):
                gr.Markdown("*(Tab 1 content — sẽ thêm ở Phase 2)*")
            with gr.Tab("Product & Channel"):
                gr.Markdown("*(Tab 2 content — sẽ thêm ở Phase 3)*")
            with gr.Tab("Geography & Customer"):
                gr.Markdown("*(Tab 3 content — sẽ thêm ở Phase 4)*")
            with gr.Tab("Explorer"):
                gr.Markdown("*(Tab 4 PyGWalker — sẽ thêm ở Phase 6)*")

        filter_inputs = [df_full_state, year_f, channel_f, region_f, product_f]
        for widget in [year_f, channel_f, region_f, product_f]:
            widget.change(
                fn=build_filter_state,
                inputs=filter_inputs,
                outputs=[df_filtered_state, filter_dict_state],
            )

        clear_btn.click(
            fn=clear_filters,
            outputs=[year_f, channel_f, region_f, product_f],
        )

    return app


if __name__ == "__main__":
    build_app().launch(inbrowser=True)
```

- [ ] **Step 2: Run app**

```bash
uv run python app.py
```
Expected: browser mở `http://localhost:7860`, thấy header đen, filter bar trắng với 4 widget + nút Clear, 4 tab với placeholder text.

- [ ] **Step 3: Manual smoke test**

- Đổi Year checkbox → không lỗi (silent state update).
- Bấm Clear Filters → cả 4 widget reset.
- Chuyển giữa 4 tab → không lỗi.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(app): skeleton with filter bar, 4 empty tabs, global state"
```

---

### Task 5: README skeleton

**Files:** Create `README.md`

- [ ] **Step 1: Create `README.md`**

```markdown
# USA Regional Sales — Interactive Gradio Dashboard

Đồ án môn **Trực quan hoá dữ liệu** — tái hiện và mở rộng Power BI dashboard phân tích sales Acme Co. 2014–2018 bằng một Gradio web app tương tác.

## Chạy local

```bash
# 1. Install deps (nếu chưa)
uv sync

# 2. Tạo .env với API key (cho nút LLM)
cp .env.example .env
# Edit .env, điền OPENAI_API_KEY=...

# 3. Chạy app
uv run python app.py
```

Mở `http://localhost:7860`.

## Architecture

Xem `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md` cho chi tiết design, `CLAUDE.md` cho codebase guide, `HANDOFF.md` cho trạng thái triển khai.

## Features

- 4 tab: Overview · Product & Channel · Geography & Customer · Explorer
- Global filter (Year / Channel / Region / Product) chia sẻ giữa 3 tab chủ đề
- 15 phân tích EDA với chart Plotly tương tác
- PyGWalker kéo-thả ở tab Explorer
- Rule-based insight tự sinh + LLM (OpenAI) strategic recommendation

## Tech stack

Python 3.11 · uv · pandas · plotly · gradio · pygwalker · openai
```

- [ ] **Step 2: Commit**

```bash
git add README.md
git commit -m "docs: initial README"
```

**Checkpoint Phase 1**: app chạy, filter có action, tab rỗng. 6 commit.

---

## Phase 2: Tab 1 Executive Overview

### Task 6: KPI aggregation functions (TDD)

**Files:** Modify `data.py`, create `tests/test_kpis.py`

- [ ] **Step 1: Write failing tests**

```python
# tests/test_kpis.py
import pandas as pd
from data import compute_kpis


def test_compute_kpis_returns_dict_with_expected_keys(df_full):
    kpis = compute_kpis(df_full)
    assert set(kpis.keys()) == {
        "total_revenue", "total_profit", "profit_margin_pct",
        "total_orders", "revenue_per_order",
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
```

- [ ] **Step 2: Run — should fail**

```bash
uv run pytest tests/test_kpis.py -v
```
Expected: ImportError for `compute_kpis`.

- [ ] **Step 3: Implement in `data.py`**

```python
# append to data.py

def compute_kpis(df: pd.DataFrame) -> dict[str, float]:
    if df.empty:
        return {
            "total_revenue": 0.0, "total_profit": 0.0,
            "profit_margin_pct": 0.0, "total_orders": 0, "revenue_per_order": 0.0,
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
```

- [ ] **Step 4: Run — pass**

```bash
uv run pytest tests/test_kpis.py -v
```
Expected: 4 passed.

- [ ] **Step 5: Commit**

```bash
git add data.py tests/test_kpis.py
git commit -m "feat(data): compute_kpis aggregation"
```

---

### Task 7: Chart builders — Tab 1 (5 charts)

**Files:**
- Create: `charts.py`
- Create: `tests/test_charts.py`

- [ ] **Step 1: Write smoke tests**

```python
# tests/test_charts.py
import plotly.graph_objects as go
from charts import (
    build_kpi_cards_html,
    build_monthly_revenue,
    build_monthly_profit,
    build_aov_histogram,
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
```

- [ ] **Step 2: Create `charts.py` with Tab 1 builders**

```python
# charts.py
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


def _empty_figure(msg: str = "Không có dữ liệu với filter hiện tại") -> go.Figure:
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
        monthly = df.groupby("order_month", as_index=False)["revenue"].sum().sort_values("order_month")
        fig = px.line(
            monthly, x="order_month", y="revenue",
            markers=True, title="Monthly Revenue Trend",
        )
        fig.update_traces(line_color=ACCENT, marker_color=ACCENT)
        fig.update_xaxes(title_text="Month")
    else:  # seasonal
        seasonal = (
            df.groupby(["order_month_num", "order_month_name"], as_index=False)["revenue"]
            .mean()
            .sort_values("order_month_num")
        )
        fig = px.bar(
            seasonal, x="order_month_name", y="revenue",
            title="Seasonal Revenue Pattern (avg across years)",
        )
        fig.update_traces(marker_color=ACCENT)
        fig.update_xaxes(title_text="Month")
    fig.update_yaxes(title_text="Revenue (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_monthly_profit(df: pd.DataFrame) -> go.Figure:
    if df.empty:
        return _empty_figure()
    monthly = df.groupby("order_month", as_index=False)["profit"].sum().sort_values("order_month")
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
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/test_charts.py -v
```
Expected: 6 passed.

- [ ] **Step 4: Commit**

```bash
git add charts.py tests/test_charts.py
git commit -m "feat(charts): Tab 1 chart builders (KPI + 4 Plotly figures)"
```

---

### Task 8: Rule-based insight — Tab 1

**Files:** Create `insights.py`, create `tests/test_insights.py`

- [ ] **Step 1: Write failing test**

```python
# tests/test_insights.py
from insights import overview_insight


def test_overview_insight_returns_markdown_with_numbers(df_full):
    text = overview_insight(df_full, filters={})
    assert isinstance(text, str)
    assert "$" in text  # có số tiền
    assert "%" in text  # có margin
    assert len(text) > 100


def test_overview_insight_empty_df():
    import pandas as pd
    empty = pd.DataFrame(columns=[
        "order_number", "revenue", "profit", "order_month_name",
        "order_month_num", "channel", "us_region", "product_name",
    ])
    text = overview_insight(empty, filters={})
    assert "Không có dữ liệu" in text
```

- [ ] **Step 2: Implement `insights.py`**

```python
# insights.py
"""Rule-based insight templates + (later) LLM client."""
from __future__ import annotations

import pandas as pd

from data import compute_kpis


def _fmt_money(v: float) -> str:
    if v >= 1e9: return f"${v/1e9:.2f}B"
    if v >= 1e6: return f"${v/1e6:.1f}M"
    if v >= 1e3: return f"${v/1e3:.1f}K"
    return f"${v:,.0f}"


def _fmt_filters(filters: dict) -> str:
    parts = []
    for key, label in [("year","Year"),("channel","Channel"),("us_region","Region"),("product_name","Product")]:
        vals = filters.get(key) or []
        if vals:
            vals_str = ", ".join(map(str, vals[:3]))
            if len(vals) > 3:
                vals_str += f" (+{len(vals)-3})"
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
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/test_insights.py -v
```
Expected: 2 passed.

- [ ] **Step 4: Commit**

```bash
git add insights.py tests/test_insights.py
git commit -m "feat(insights): rule-based overview_insight (Tab 1)"
```

---

### Task 9: Wire Tab 1 into `app.py`

**Files:** Modify `app.py`

- [ ] **Step 1: Replace Tab 1 placeholder and wire events**

In `app.py`, replace `with gr.Tab("Overview"):` block and add imports at top:

```python
# top of app.py
from charts import (
    build_kpi_cards_html, build_monthly_revenue, build_monthly_profit,
    build_aov_histogram, build_price_margin_scatter,
)
from insights import overview_insight
```

Replace the Tab 1 block:

```python
with gr.Tab("Overview"):
    kpi_html = gr.HTML(build_kpi_cards_html(df_full))
    with gr.Row():
        monthly_rev_mode = gr.Radio(
            ["timeseries", "seasonal"], value="timeseries",
            label="Monthly Revenue view", scale=1,
        )
    with gr.Row():
        monthly_rev_chart = gr.Plot(build_monthly_revenue(df_full, "timeseries"))
        monthly_profit_chart = gr.Plot(build_monthly_profit(df_full))
    with gr.Row():
        aov_chart = gr.Plot(build_aov_histogram(df_full))
        scatter_chart = gr.Plot(build_price_margin_scatter(df_full))
    tab1_insight = gr.Markdown(
        overview_insight(df_full, {}), elem_classes=["insight-panel"],
    )
```

- [ ] **Step 2: Add render function + wire filter changes**

Below tab definitions, add:

```python
def render_tab1(df_filtered: pd.DataFrame, filters: dict, rev_mode: str):
    return (
        build_kpi_cards_html(df_filtered),
        build_monthly_revenue(df_filtered, rev_mode),
        build_monthly_profit(df_filtered),
        build_aov_histogram(df_filtered),
        build_price_margin_scatter(df_filtered),
        overview_insight(df_filtered, filters),
    )
```

Put this function inside `build_app()` (needs access to local scope) or at module level (takes df as arg). Place at module level.

Then wire in the filter-change chain — after `widget.change(fn=build_filter_state, ...)` add `.then(...)`:

```python
for widget in [year_f, channel_f, region_f, product_f]:
    widget.change(
        fn=build_filter_state,
        inputs=filter_inputs,
        outputs=[df_filtered_state, filter_dict_state],
    ).then(
        fn=render_tab1,
        inputs=[df_filtered_state, filter_dict_state, monthly_rev_mode],
        outputs=[kpi_html, monthly_rev_chart, monthly_profit_chart,
                 aov_chart, scatter_chart, tab1_insight],
    )

# Also handle radio change for monthly_rev_mode
monthly_rev_mode.change(
    fn=render_tab1,
    inputs=[df_filtered_state, filter_dict_state, monthly_rev_mode],
    outputs=[kpi_html, monthly_rev_chart, monthly_profit_chart,
             aov_chart, scatter_chart, tab1_insight],
)

# Handle Clear button — chain reset + re-render
clear_btn.click(
    fn=clear_filters,
    outputs=[year_f, channel_f, region_f, product_f],
).then(
    fn=build_filter_state,
    inputs=filter_inputs,
    outputs=[df_filtered_state, filter_dict_state],
).then(
    fn=render_tab1,
    inputs=[df_filtered_state, filter_dict_state, monthly_rev_mode],
    outputs=[kpi_html, monthly_rev_chart, monthly_profit_chart,
             aov_chart, scatter_chart, tab1_insight],
)
```

- [ ] **Step 3: Manual smoke test**

```bash
uv run python app.py
```
Expected:
- Tab 1 hiển thị 5 KPI card + Monthly Revenue line + Monthly Profit line + AOV histogram + Price/Margin scatter + insight markdown.
- Đổi Year=2017 → tất cả chart + insight update theo.
- Đổi Radio "seasonal" → Monthly Revenue chart chuyển sang bar chart seasonal.
- Bấm Clear → filter reset, chart quay lại full data.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(app): wire Tab 1 Overview with filter + radio reactivity"
```

**Checkpoint Phase 2**: Tab 1 full chức năng. App demo-able end-to-end.

---

### Task 10: Full regression test after Phase 2

- [ ] **Step 1: Run all tests**

```bash
uv run pytest -v
```
Expected: all green (at least 15 tests now).

- [ ] **Step 2: Manual checklist**

- [ ] App boot `uv run python app.py` < 3s.
- [ ] Tab 1 shows 5 KPI cards with numbers.
- [ ] Filter Year=[2017] → KPI và chart update.
- [ ] Filter Channel=[Export] → update.
- [ ] Filter empty (deselect tất cả Year) → panel "Không có dữ liệu".

---

## Phase 3: Tab 2 Product & Channel

### Task 11: Chart builders — Tab 2 (5 charts)

**Files:** Modify `charts.py`, modify `tests/test_charts.py`

- [ ] **Step 1: Write tests**

```python
# append to tests/test_charts.py
from charts import (
    build_top_products_revenue, build_top_products_profit,
    build_channel_pie, build_margin_by_channel, build_price_boxplot,
)


def test_top_products_revenue(df_full):
    fig = build_top_products_revenue(df_full)
    assert isinstance(fig, go.Figure)


def test_top_products_profit(df_full):
    fig = build_top_products_profit(df_full)
    assert isinstance(fig, go.Figure)


def test_channel_pie(df_full):
    fig = build_channel_pie(df_full)
    assert isinstance(fig, go.Figure)


def test_margin_by_channel(df_full):
    fig = build_margin_by_channel(df_full)
    assert isinstance(fig, go.Figure)


def test_price_boxplot(df_full):
    fig = build_price_boxplot(df_full)
    assert isinstance(fig, go.Figure)
```

- [ ] **Step 2: Implement in `charts.py`**

```python
# append to charts.py

def build_top_products_revenue(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty: return _empty_figure()
    top = df.groupby("product_name", as_index=False)["revenue"].sum().nlargest(n, "revenue")
    fig = px.bar(top, x="revenue", y="product_name", orientation="h",
                 title=f"Top {n} Products by Revenue")
    fig.update_traces(marker_color=ACCENT)
    fig.update_yaxes(categoryorder="total ascending", title_text="")
    fig.update_xaxes(title_text="Revenue (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_top_products_profit(df: pd.DataFrame, n: int = 10) -> go.Figure:
    if df.empty: return _empty_figure()
    top = df.groupby("product_name", as_index=False)["profit"].mean().nlargest(n, "profit")
    fig = px.bar(top, x="profit", y="product_name", orientation="h",
                 title=f"Top {n} Products by Avg Profit per Order Line")
    fig.update_traces(marker_color="#2e7d32")
    fig.update_yaxes(categoryorder="total ascending", title_text="")
    fig.update_xaxes(title_text="Avg Profit (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_channel_pie(df: pd.DataFrame) -> go.Figure:
    if df.empty: return _empty_figure()
    by_ch = df.groupby("channel", as_index=False)["revenue"].sum()
    fig = px.pie(by_ch, names="channel", values="revenue", hole=0.4,
                 title="Revenue Share by Channel",
                 color_discrete_sequence=[ACCENT, ACCENT_SOFT, "#2e7d32"])
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_margin_by_channel(df: pd.DataFrame) -> go.Figure:
    if df.empty: return _empty_figure()
    by_ch = df.groupby("channel", as_index=False)["profit_margin_pct"].mean().sort_values("profit_margin_pct", ascending=False)
    fig = px.bar(by_ch, x="channel", y="profit_margin_pct",
                 title="Avg Profit Margin % by Channel",
                 text="profit_margin_pct")
    fig.update_traces(marker_color=ACCENT, texttemplate="%{text:.1f}%", textposition="outside")
    fig.update_yaxes(title_text="Margin %")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_price_boxplot(df: pd.DataFrame) -> go.Figure:
    if df.empty: return _empty_figure()
    fig = px.box(df, x="product_name", y="unit_price",
                 title="Unit Price Distribution per Product")
    fig.update_traces(marker_color=ACCENT)
    fig.update_xaxes(title_text="", tickangle=-45)
    fig.update_yaxes(title_text="Unit Price (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig
```

- [ ] **Step 3: Run tests**

```bash
uv run pytest tests/test_charts.py -v
```
Expected: 11 passed (6 old + 5 new).

- [ ] **Step 4: Commit**

```bash
git add charts.py tests/test_charts.py
git commit -m "feat(charts): Tab 2 builders (products, channel, boxplot)"
```

---

### Task 12: Rule-based insight — Tab 2

**Files:** Modify `insights.py`, modify `tests/test_insights.py`

- [ ] **Step 1: Test**

```python
# append to tests/test_insights.py
from insights import product_channel_insight


def test_product_channel_insight(df_full):
    text = product_channel_insight(df_full, filters={})
    assert "Wholesale" in text or "Distributor" in text or "Export" in text
    assert "Product" in text
```

- [ ] **Step 2: Implement**

```python
# append to insights.py

def product_channel_insight(df: pd.DataFrame, filters: dict) -> str:
    if df.empty:
        return "> Không có dữ liệu."

    top_product = df.groupby("product_name")["revenue"].sum().idxmax()
    top_product_rev = df.groupby("product_name")["revenue"].sum().max()

    top_channel_row = df.groupby("channel")["revenue"].sum().sort_values(ascending=False)
    top_channel = top_channel_row.index[0]
    top_channel_pct = top_channel_row.iloc[0] / top_channel_row.sum() * 100

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
```

- [ ] **Step 3: Run tests + commit**

```bash
uv run pytest tests/test_insights.py -v
git add insights.py tests/test_insights.py
git commit -m "feat(insights): product_channel_insight (Tab 2)"
```

---

### Task 13: Wire Tab 2 in `app.py`

**Files:** Modify `app.py`

- [ ] **Step 1: Import + replace Tab 2 placeholder**

Add to imports:
```python
from charts import (
    build_top_products_revenue, build_top_products_profit,
    build_channel_pie, build_margin_by_channel, build_price_boxplot,
)
from insights import product_channel_insight
```

Replace Tab 2 block:

```python
with gr.Tab("Product & Channel"):
    with gr.Row():
        tp_rev_chart = gr.Plot(build_top_products_revenue(df_full))
        tp_profit_chart = gr.Plot(build_top_products_profit(df_full))
    with gr.Row():
        ch_pie_chart = gr.Plot(build_channel_pie(df_full))
        ch_margin_chart = gr.Plot(build_margin_by_channel(df_full))
    price_box_chart = gr.Plot(build_price_boxplot(df_full))
    tab2_insight = gr.Markdown(
        product_channel_insight(df_full, {}), elem_classes=["insight-panel"],
    )
```

- [ ] **Step 2: Add `render_tab2` + wire into filter chain**

Add module-level function:

```python
def render_tab2(df_filtered: pd.DataFrame, filters: dict):
    return (
        build_top_products_revenue(df_filtered),
        build_top_products_profit(df_filtered),
        build_channel_pie(df_filtered),
        build_margin_by_channel(df_filtered),
        build_price_boxplot(df_filtered),
        product_channel_insight(df_filtered, filters),
    )
```

Extend the `.then()` chain after each filter widget's `.change()` AND after `clear_btn.click()`:

```python
.then(
    fn=render_tab2,
    inputs=[df_filtered_state, filter_dict_state],
    outputs=[tp_rev_chart, tp_profit_chart, ch_pie_chart, ch_margin_chart,
             price_box_chart, tab2_insight],
)
```

(Chain thêm `.then()` sau `.then()` của Tab 1 — Gradio hỗ trợ chained event.)

- [ ] **Step 3: Smoke test**

```bash
uv run python app.py
```
Expected:
- Tab 2 hiển thị 4 chart (2 row 2 col) + boxplot full width + insight.
- Đổi filter → Tab 2 update đồng thời với Tab 1.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(app): wire Tab 2 Product & Channel"
```

---

### Task 14: Regression test after Phase 3

- [ ] **Step 1: pytest all**

```bash
uv run pytest -v
```
Expected: ~20 tests pass.

- [ ] **Step 2: Manual smoke** — đổi filter, kiểm tra cả 2 tab reactive.

---

## Phase 4: Tab 3 Geography & Customer

### Task 15: Chart builders — Tab 3 (6 charts)

**Files:** Modify `charts.py`, `tests/test_charts.py`

- [ ] **Step 1: Tests**

```python
# append to tests/test_charts.py
from charts import (
    build_region_bar, build_state_choropleth, build_states_dual_bar,
    build_customer_bar, build_customer_bubble, build_correlation_heatmap,
)


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
```

- [ ] **Step 2: Implement**

```python
# append to charts.py

def build_region_bar(df: pd.DataFrame) -> go.Figure:
    if df.empty: return _empty_figure()
    by_reg = df.groupby("us_region", as_index=False)["revenue"].sum().sort_values("revenue", ascending=True)
    fig = px.bar(by_reg, x="revenue", y="us_region", orientation="h",
                 title="Revenue by US Region")
    fig.update_traces(marker_color=ACCENT)
    fig.update_xaxes(title_text="Revenue (USD)")
    fig.update_yaxes(title_text="")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_state_choropleth(df: pd.DataFrame) -> go.Figure:
    if df.empty: return _empty_figure()
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
    if df.empty: return _empty_figure()
    by_state = df.groupby("state_name").agg(
        revenue=("revenue", "sum"),
        orders=("order_number", "nunique"),
    ).reset_index().nlargest(n, "revenue").sort_values("revenue")
    fig = go.Figure()
    fig.add_trace(go.Bar(y=by_state["state_name"], x=by_state["revenue"],
                         orientation="h", name="Revenue", marker_color=ACCENT))
    fig.add_trace(go.Bar(y=by_state["state_name"], x=by_state["orders"],
                         orientation="h", name="Orders", marker_color=ACCENT_SOFT,
                         xaxis="x2"))
    fig.update_layout(
        title=f"Top {n} States — Revenue + Orders",
        xaxis=dict(title="Revenue (USD)", side="bottom"),
        xaxis2=dict(title="Orders", overlaying="x", side="top"),
        barmode="group",
        **PLOTLY_LAYOUT,
    )
    return fig


def build_customer_bar(df: pd.DataFrame, mode: str = "top", n: int = 10) -> go.Figure:
    if df.empty: return _empty_figure()
    grp = df.groupby("customer_name", as_index=False)["revenue"].sum()
    if mode == "top":
        selected = grp.nlargest(n, "revenue")
        title = f"Top {n} Customers by Revenue"
    else:
        selected = grp.nsmallest(n, "revenue")
        title = f"Bottom {n} Customers by Revenue"
    selected = selected.sort_values("revenue", ascending=(mode == "top"))
    fig = px.bar(selected, x="revenue", y="customer_name", orientation="h", title=title)
    fig.update_traces(marker_color=ACCENT if mode == "top" else "#ed6c02")
    fig.update_yaxes(title_text="")
    fig.update_xaxes(title_text="Revenue (USD)")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_customer_bubble(df: pd.DataFrame) -> go.Figure:
    if df.empty: return _empty_figure()
    seg = df.groupby("customer_name").agg(
        total_revenue=("revenue", "sum"),
        avg_margin=("profit_margin_pct", "mean"),
        n_orders=("order_number", "nunique"),
    ).reset_index()
    fig = px.scatter(
        seg, x="total_revenue", y="avg_margin", size="n_orders",
        hover_name="customer_name", size_max=40,
        title="Customer Segmentation (Revenue × Margin × Orders)",
    )
    fig.update_traces(marker_color=ACCENT, marker_line=dict(color=HEADER, width=0.5))
    fig.update_xaxes(title_text="Total Revenue (USD)")
    fig.update_yaxes(title_text="Avg Profit Margin %")
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig


def build_correlation_heatmap(df: pd.DataFrame) -> go.Figure:
    if df.empty: return _empty_figure()
    cols = ["quantity", "unit_price", "revenue", "cost", "profit"]
    corr = df[cols].corr()
    fig = px.imshow(
        corr, text_auto=".2f", aspect="auto", color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1, title="Correlation Heatmap",
    )
    fig.update_layout(**PLOTLY_LAYOUT)
    return fig
```

- [ ] **Step 3: Run tests + commit**

```bash
uv run pytest tests/test_charts.py -v
git add charts.py tests/test_charts.py
git commit -m "feat(charts): Tab 3 builders (region, map, states, customers, bubble, heatmap)"
```

---

### Task 16: Rule-based insight — Tab 3

**Files:** Modify `insights.py`, `tests/test_insights.py`

- [ ] **Step 1: Test**

```python
# append to tests/test_insights.py
from insights import geo_customer_insight


def test_geo_customer_insight(df_full):
    text = geo_customer_insight(df_full, filters={})
    assert "California" in text or "CA" in text or "West" in text or "Midwest" in text
```

- [ ] **Step 2: Implement**

```python
# append to insights.py

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
```

- [ ] **Step 3: Run + commit**

```bash
uv run pytest tests/test_insights.py -v
git add insights.py tests/test_insights.py
git commit -m "feat(insights): geo_customer_insight (Tab 3)"
```

---

### Task 17: Wire Tab 3 + Top/Bottom toggle

**Files:** Modify `app.py`

- [ ] **Step 1: Imports**

```python
from charts import (
    build_region_bar, build_state_choropleth, build_states_dual_bar,
    build_customer_bar, build_customer_bubble, build_correlation_heatmap,
)
from insights import geo_customer_insight
```

- [ ] **Step 2: Replace Tab 3 placeholder**

```python
with gr.Tab("Geography & Customer"):
    with gr.Row():
        region_chart = gr.Plot(build_region_bar(df_full))
        map_chart = gr.Plot(build_state_choropleth(df_full))
    states_dual_chart = gr.Plot(build_states_dual_bar(df_full))
    with gr.Row():
        with gr.Column():
            customer_mode = gr.Radio(
                ["top", "bottom"], value="top", label="Customer view",
            )
            customer_bar_chart = gr.Plot(build_customer_bar(df_full, "top"))
        bubble_chart = gr.Plot(build_customer_bubble(df_full))
    with gr.Row():
        heatmap_chart = gr.Plot(build_correlation_heatmap(df_full))
        tab3_insight = gr.Markdown(
            geo_customer_insight(df_full, {}), elem_classes=["insight-panel"],
        )
```

- [ ] **Step 3: Add `render_tab3`**

```python
def render_tab3(df_filtered, filters, cust_mode):
    return (
        build_region_bar(df_filtered),
        build_state_choropleth(df_filtered),
        build_states_dual_bar(df_filtered),
        build_customer_bar(df_filtered, cust_mode),
        build_customer_bubble(df_filtered),
        build_correlation_heatmap(df_filtered),
        geo_customer_insight(df_filtered, filters),
    )
```

- [ ] **Step 4: Wire into filter chain + customer_mode radio**

Extend the chain:

```python
.then(
    fn=render_tab3,
    inputs=[df_filtered_state, filter_dict_state, customer_mode],
    outputs=[region_chart, map_chart, states_dual_chart, customer_bar_chart,
             bubble_chart, heatmap_chart, tab3_insight],
)
```

Customer mode change handler:

```python
customer_mode.change(
    fn=render_tab3,
    inputs=[df_filtered_state, filter_dict_state, customer_mode],
    outputs=[region_chart, map_chart, states_dual_chart, customer_bar_chart,
             bubble_chart, heatmap_chart, tab3_insight],
)
```

- [ ] **Step 5: Smoke test**

```bash
uv run python app.py
```
Expected:
- Tab 3 có 6 chart + radio top/bottom + insight.
- Đổi Top → Bottom: chart customer đổi.
- Choropleth map render đúng USA states.
- Filter đổi: cả 3 tab cập nhật.

- [ ] **Step 6: Commit**

```bash
git add app.py
git commit -m "feat(app): wire Tab 3 Geo & Customer with Top/Bottom toggle"
```

---

### Task 18: Regression after Phase 4

- [ ] Run `uv run pytest -v` → ~28 tests pass.
- [ ] Manual: all 3 themed tabs reactive to global filter.

---

## Phase 5: LLM Integration

### Task 19: `summarize_for_llm` in `data.py` + OpenAI client in `insights.py`

**Files:** Modify `data.py`, `insights.py`, `tests/test_insights.py`

- [ ] **Step 1: Tests**

```python
# append to tests/test_insights.py
import os
import pytest
from insights import summarize_for_llm, llm_recommendation


def test_summarize_for_llm_returns_dict(df_full):
    from data import summarize_for_llm as _s  # fail import test — function phải ở data.py
    s = _s(df_full, filters={"year": [2017]}, focus="overview")
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
```

- [ ] **Step 2: `summarize_for_llm` in `data.py`**

```python
# append to data.py
from typing import Literal


def summarize_for_llm(
    df: pd.DataFrame,
    filters: dict,
    focus: Literal["overview", "product_channel", "geo_customer"],
) -> dict:
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
    peak_month = (
        df.groupby(["order_month_num", "order_month_name"])["revenue"]
        .sum().idxmax()
    )

    return {
        "filters": filters,
        "focus": focus,
        "kpis": {k_: round(v, 2) if isinstance(v, float) else v for k_, v in k.items()},
        "top_products": top_products,
        "top_channels": top_channels,
        "top_regions": top_regions,
        "top_states": top_states,
        "peak_month": peak_month[1],
    }
```

- [ ] **Step 3: LLM client in `insights.py`**

```python
# append to insights.py
import json
import os
from typing import Literal

from dotenv import load_dotenv

load_dotenv()

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
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return (
            "> **⚠ Missing OPENAI_API_KEY.** Tạo file `.env` từ `.env.example` "
            "và điền key của bạn để dùng tính năng này."
        )

    from data import summarize_for_llm
    summary = summarize_for_llm(df, filters, focus)

    try:
        from openai import OpenAI
        client = OpenAI(api_key=api_key)
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

        system = (
            "Bạn là senior sales data analyst. Hãy đưa 3–5 khuyến nghị chiến lược "
            "ngắn gọn, hành động được, dựa trên số liệu thật trong data summary. "
            "Mỗi bullet ≤ 2 câu, tiếng Việt, có kèm số liệu cụ thể (dollar, %, tên "
            "sản phẩm/vùng/kênh). Không bịa thông tin ngoài data summary."
        )
        user = (
            f"Trọng tâm phân tích: **{focus}**.\n"
            f"Gợi ý: {_FOCUS_HINTS[focus]}\n\n"
            f"Data summary (JSON):\n```json\n{json.dumps(summary, ensure_ascii=False, indent=2)}\n```\n\n"
            f"Trả về **Markdown** với heading '### Strategic Recommendations' và "
            f"danh sách bullet."
        )

        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": system},
                      {"role": "user", "content": user}],
            temperature=0.4,
            max_tokens=600,
            timeout=15,
        )
        return resp.choices[0].message.content or "(empty response)"
    except Exception as e:
        return f"> **⚠ LLM call failed:** `{type(e).__name__}: {e}`"
```

- [ ] **Step 4: Run tests**

```bash
uv run pytest tests/test_insights.py -v
```
Expected: all pass (LLM test skipped if no key, error-path test uses monkeypatch).

- [ ] **Step 5: Commit**

```bash
git add data.py insights.py tests/test_insights.py
git commit -m "feat(insights): OpenAI LLM recommendation + summarize_for_llm"
```

---

### Task 20: Wire LLM button into Tab 1/2/3

**Files:** Modify `app.py`

- [ ] **Step 1: Import + add button + output to each tab**

```python
from insights import llm_recommendation
```

In Tab 1 block, after `tab1_insight`:

```python
with gr.Row():
    tab1_llm_btn = gr.Button("Sinh Strategic Recommendation (AI)", variant="primary")
tab1_llm_output = gr.Markdown(elem_classes=["llm-output"])
```

In Tab 2 (similar):
```python
tab2_llm_btn = gr.Button("Sinh Strategic Recommendation (AI)", variant="primary")
tab2_llm_output = gr.Markdown(elem_classes=["llm-output"])
```

In Tab 3 (similar):
```python
tab3_llm_btn = gr.Button("Sinh Strategic Recommendation (AI)", variant="primary")
tab3_llm_output = gr.Markdown(elem_classes=["llm-output"])
```

- [ ] **Step 2: Wire click handlers**

```python
tab1_llm_btn.click(
    fn=lambda df, f: llm_recommendation(df, f, "overview"),
    inputs=[df_filtered_state, filter_dict_state],
    outputs=tab1_llm_output,
)
tab2_llm_btn.click(
    fn=lambda df, f: llm_recommendation(df, f, "product_channel"),
    inputs=[df_filtered_state, filter_dict_state],
    outputs=tab2_llm_output,
)
tab3_llm_btn.click(
    fn=lambda df, f: llm_recommendation(df, f, "geo_customer"),
    inputs=[df_filtered_state, filter_dict_state],
    outputs=tab3_llm_output,
)
```

- [ ] **Step 3: Test with + without API key**

Without `.env`:
```bash
uv run python app.py
# Bấm nút LLM → output hiển thị "⚠ Missing OPENAI_API_KEY"
```

With `.env` (paste real key vào `.env`):
```bash
uv run python app.py
# Bấm nút LLM Tab 1 → chờ ~5-8s → hiển thị 3-5 bullet tiếng Việt.
```

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(app): LLM button on Tab 1/2/3 with on-demand OpenAI call"
```

---

### Task 21: Regression after Phase 5

- [ ] `uv run pytest -v`
- [ ] Manual: demo full flow — filter → 3 tab reactive → bấm 3 LLM button → kết quả hợp lệ.

---

## Phase 6: Tab 4 Explorer (PyGWalker)

### Task 22: Verify PyGWalker + Gradio compatibility

**Files:** Create `scripts/check_pygwalker.py` (throwaway)

- [ ] **Step 1: Quick compatibility check**

```python
# scripts/check_pygwalker.py
"""Dùng để verify pygwalker import và có API cho Gradio. Xoá sau khi xác nhận."""
import pygwalker as pyg
import pandas as pd

print("pygwalker version:", pyg.__version__)

# Method 1: static html
from data import load_csv
df = load_csv()
try:
    from pygwalker.api.html import to_html
    html = to_html(df.head(1000))
    print("to_html ok, length:", len(html))
except Exception as e:
    print("to_html error:", e)
```

```bash
mkdir -p scripts
# (tạo file trên)
uv run python scripts/check_pygwalker.py
```

- [ ] **Step 2: Decide integration path**

Based on output:
- Nếu `to_html()` trả HTML string → dùng `gr.HTML` component.
- Nếu PyGWalker có `.api.gradio` module → dùng trực tiếp.
- Nếu không method nào khả dụng → fallback mini-explorer (xem Task 23 fallback).

- [ ] **Step 3: Clean up script, document finding in HANDOFF.md**

Update `HANDOFF.md` dưới "Ghi chú kỹ thuật quan trọng":
```
- PyGWalker integration: [CHỌN 1]
  - [ ] via `to_html()` + `gr.HTML` component
  - [ ] via `pygwalker.api.gradio` module
  - [ ] FALLBACK: custom mini-explorer (dropdown dimension/measure/chart)
```

- [ ] **Step 4: Remove check script**

```bash
rm -rf scripts/
```

---

### Task 23: Implement Explorer tab

**Files:** Modify `app.py`

- [ ] **Step 1: Option A — PyGWalker HTML integration**

In `app.py`, replace Tab 4 placeholder:

```python
with gr.Tab("Explorer"):
    gr.Markdown(
        "### Data Explorer — PyGWalker\n"
        "Kéo-thả dimension/measure để khám phá dữ liệu tự do. "
        "Dataset đã được áp global filter khi bạn mở tab này. "
        "PyGWalker có filter riêng ngay trong component."
    )
    explorer_html = gr.HTML(label="Explorer")

def render_explorer(df_filtered):
    try:
        from pygwalker.api.html import to_html
        return to_html(df_filtered, spec_io_mode="rw")
    except Exception as e:
        return f"<div style='padding:24px;color:#a33;'>PyGWalker error: {e}</div>"

# Initial render
explorer_html.value = render_explorer(df_full)

# Wire to tab selection (re-render khi user chuyển vào tab)
tabs.select(
    fn=lambda df: render_explorer(df),
    inputs=[df_filtered_state],
    outputs=[explorer_html],
)
```

Nếu `pygwalker.api.html` không có, dùng fallback (Step 2).

- [ ] **Step 2: Option B — FALLBACK mini-explorer (nếu PyGWalker không tương thích)**

Replace Tab 4:

```python
with gr.Tab("Explorer"):
    gr.Markdown("### Custom Explorer\nChọn dimension/measure/chart type để khám phá.")
    with gr.Row():
        dim_x = gr.Dropdown(
            ["channel", "us_region", "order_month_name", "product_name", "state_name"],
            value="channel", label="Dimension (X)",
        )
        measure = gr.Dropdown(
            ["revenue", "profit", "quantity", "profit_margin_pct"],
            value="revenue", label="Measure (Y)",
        )
        agg = gr.Dropdown(["sum", "mean", "median", "count"], value="sum", label="Aggregation")
        chart_type = gr.Dropdown(["bar", "line", "scatter", "box"], value="bar", label="Chart type")
    explorer_plot = gr.Plot()

    def custom_explorer(df, x, m, a, ctype):
        import plotly.express as px
        if df.empty or not x or not m:
            return _empty_figure()
        if a == "count":
            data = df.groupby(x).size().reset_index(name=m)
        else:
            data = df.groupby(x, as_index=False)[m].agg(a)
        fn = {"bar": px.bar, "line": px.line, "scatter": px.scatter, "box": px.box}[ctype]
        fig = fn(data, x=x, y=m, title=f"{a}({m}) by {x}")
        fig.update_layout(**PLOTLY_LAYOUT)
        return fig

    for widget in [dim_x, measure, agg, chart_type]:
        widget.change(
            fn=custom_explorer,
            inputs=[df_filtered_state, dim_x, measure, agg, chart_type],
            outputs=[explorer_plot],
        )
```

Note: `_empty_figure` và `PLOTLY_LAYOUT` cần import từ `charts.py`.

- [ ] **Step 3: Smoke test**

```bash
uv run python app.py
```
Expected:
- Option A: tab Explorer hiển thị PyGWalker UI, kéo-thả được field.
- Option B: 4 dropdown + chart render theo lựa chọn.

- [ ] **Step 4: Commit**

```bash
git add app.py
git commit -m "feat(app): Explorer tab (PyGWalker or fallback mini-explorer)"
```

**Checkpoint Phase 6**: 4 tab đầy đủ, demo sẵn sàng.

---

## Phase 7: Polish & Docs

### Task 24: Empty-filter edge case regression

**Files:** Modify `app.py` (if needed), manual test

- [ ] **Step 1: Test edge cases manually**

- [ ] Deselect TẤT CẢ Year → KPI, chart Tab 1/2/3 hiển thị "Không có dữ liệu".
- [ ] Filter combination 0 rows (vd. Year=[2014], Channel=[Export], Region=[Midwest]) → graceful.
- [ ] Chọn product lạ (nếu có bug) → filter vẫn work.
- [ ] LLM button với empty df → output "Không có dữ liệu".

- [ ] **Step 2: Fix any crashes by adding `if df.empty:` guards** ở chart builder nếu miss.

- [ ] **Step 3: Commit nếu có fix**

```bash
git add -A
git commit -m "fix: empty-filter guards in chart builders"
```

---

### Task 25: CSS polish + layout refinement

**Files:** Modify `theme.py`, `app.py`

- [ ] **Step 1: Review visual on browser**

Open app, check:
- Card bo tròn, shadow đều.
- Header đen với accent underline.
- Filter bar có khoảng cách hợp lý.
- Chart không sát nhau.
- Text insight có background nhạt.

- [ ] **Step 2: Tinh chỉnh CSS trong `theme.py`** (spacing, margin, font-size dựa trên review).

- [ ] **Step 3: Test ở 2 kích thước màn hình**

- [ ] 1440×900 (laptop)
- [ ] 1920×1080 (desktop) 

- [ ] **Step 4: Commit**

```bash
git add theme.py app.py
git commit -m "style: CSS polish — spacing, responsive layout tweaks"
```

---

### Task 26: Full README with screenshot

**Files:** Modify `README.md`

- [ ] **Step 1: Take screenshot**

Chạy app, mở browser, chụp Tab 1 full + Tab 3 (có map) → lưu `docs/screenshots/tab1.png`, `docs/screenshots/tab3.png`.

```bash
mkdir -p docs/screenshots
# screenshot tay
```

- [ ] **Step 2: Expand README**

```markdown
# USA Regional Sales — Interactive Gradio Dashboard

![Tab 1 Overview](docs/screenshots/tab1.png)

Đồ án môn **Trực quan hoá dữ liệu** — Gradio web app thay thế Power BI, tái hiện 15 phân tích EDA + 5 KPI card + tab Explorer tự do + nút AI sinh khuyến nghị chiến lược.

## Tính năng

- **4 tab**: Overview · Product & Channel · Geography & Customer · Explorer
- **Global filter** (Year · Channel · Region · Product) chia sẻ 3 tab chủ đề
- **15 phân tích EDA** bằng Plotly tương tác (line, bar, pie, histogram, scatter, boxplot, choropleth, bubble, heatmap)
- **Toggle**: Monthly Revenue time-series ↔ seasonal pattern · Top 10 ↔ Bottom 10 customers
- **Rule-based insight** tự động sinh theo filter hiện tại
- **AI Strategic Recommendation**: nút trên mỗi tab gọi OpenAI GPT sinh 3–5 bullet khuyến nghị
- **Explorer tab**: PyGWalker kéo-thả (hoặc fallback mini-explorer nếu không tương thích)

## Cài đặt

```bash
uv sync                    # install deps
cp .env.example .env       # tạo .env
# Edit .env: OPENAI_API_KEY=sk-...
```

## Chạy

```bash
uv run python app.py
# → http://localhost:7860
```

## Test

```bash
uv run pytest -v
```

## Architecture

| Module | Trách nhiệm |
|---|---|
| `app.py` | Gradio Blocks UI, event handler, state |
| `data.py` | Load CSV, filter, aggregate KPI, summarize cho LLM |
| `charts.py` | 16 chart builders (pure functions, trả Plotly Figure) |
| `insights.py` | Rule-based template + OpenAI client |
| `theme.py` | CSS + color palette |

Chi tiết xem `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md`.

## Tech stack

Python 3.11 · uv · pandas · plotly · gradio · pygwalker · openai · python-dotenv · pytest
```

- [ ] **Step 3: Commit**

```bash
git add README.md docs/screenshots/
git commit -m "docs: README with screenshot + feature list"
```

---

### Task 27: Update HANDOFF.md progress

**Files:** Modify `HANDOFF.md`

- [ ] **Step 1: Update status table**

Tất cả phase 1-7 mark ✓ done. Phase 8 = deferred.

- [ ] **Step 2: Update changelog**

Thêm dòng date/changes.

- [ ] **Step 3: Commit**

```bash
git add HANDOFF.md
git commit -m "docs: update HANDOFF progress after Phase 7"
```

---

### Task 28: Final acceptance test

- [ ] **Step 1: Fresh boot test**

```bash
uv run python app.py
```
Expected boot < 3s.

- [ ] **Step 2: Checklist 8 success criteria (từ spec)**

- [ ] 1. Boot ≤ 3s ✓
- [ ] 2. Filter change → tất cả update ≤ 1s ✓
- [ ] 3. 15 EDA analyses hiển thị đầy đủ (kiểm 3 tab) ✓
- [ ] 4. LLM button ≤ 10s ✓ (với API key)
- [ ] 5. Không có API key → báo lỗi rõ ràng ✓
- [ ] 6. Explorer tab hoạt động ✓
- [ ] 7. Custom CSS áp dụng ✓
- [ ] 8. Filter 0 rows → "Không có dữ liệu" ✓

- [ ] **Step 3: Final commit**

```bash
git add -A
git commit -m "chore: final polish for submission"
```

---

## Phase 8 (Stretch): Upload CSV

### Task 29: Schema validator

**Files:** Modify `data.py`, `tests/test_data.py`

- [ ] **Step 1: Tests + impl of `validate_schema(df)` → raise với message rõ ràng nếu thiếu cột.**
- [ ] **Step 2: Wire `gr.File` upload component + "Load uploaded" button trong filter bar.**
- [ ] **Step 3: Update HANDOFF.md + commit.**

### Task 30: Integration test with alternate CSV

- [ ] Thử với một CSV khác (subset của original) — app phải load được hoặc báo lỗi schema cụ thể.

---

## End of plan

**Expected total commits**: ~25–30, trên main branch.
**Expected total tests**: ~30.
**Delivery**: app chạy 1 lệnh `uv run python app.py`, demo 10–15 phút cho giảng viên.
