# CLAUDE.md

This file provides guidance to Claude Code when working with this repository.

## Repository nature

**Data analytics portfolio project** — USA Regional Sales Analysis, 2014–2018 (Acme Co.).
Two deliverables, both complete:

1. **Jupyter notebook EDA** — cleans 6-sheet Excel, merges, feature-engineers, exports CSV.
2. **Gradio web app** — interactive dashboard on top of the CSV (replaces Power BI for the course).

Documentation files (`Summary.txt`, `USA_Regional_Sales_Analysis_Project_Documentation.txt`) are in Vietnamese. Code and comments are in English.

---

## Data pipeline

```
Regional Sales Dataset.xlsx       (source: 6 sheets)
    └─► EDA_Regional_Sales_Analysis.ipynb  (clean → merge → feature-engineer → EDA)
            └─► Sales_data(EDA Exported).csv   (64,104 rows × 21 cols)
                    ├─► SALES REPORT.pbix       (Power BI dashboard, 3 pages — static)
                    └─► app.py (Gradio)          (interactive web app — primary deliverable)
```

**Critical:** The CSV is the single shared source for both Power BI and Gradio. Regenerate it (re-run Cell 75) before refreshing either.

---

## Notebook architecture (`EDA_Regional_Sales_Analysis.ipynb`)

80 cells. Written for **Google Colab** — Cell 10 has `drive.mount(...)`. Replace with local `file_path` to run locally.

| Cell range | Phase | Notes |
|---|---|---|
| 8–10 | Import + load | `pd.read_excel(sheet_name=None)` reads all 6 sheets into a dict |
| 11–18 | Data profiling | Null/dtype/duplicate checks; fix `State Regions` header-in-row-0 bug |
| 19 | Merge pipeline | 5 consecutive left joins — do not change join type |
| 20–25 | Cleaning | Drop redundant columns, snake_case rename, null out non-2017 budget |
| 26 | Feature engineering | `total_cost`, `profit`, `profit_margin_pct`, `order_month_name`, `order_month_num` |
| 32 | Filter 2018 | Drop Jan–Feb 2018 (partial year skews seasonality) |
| 33–74 | 15 EDA analyses | Temporal, univariate, bivariate, multivariate, geospatial |
| 75 | Export CSV | Output consumed by Power BI and Gradio app |

---

## Data model (ERD)

`Sales Orders` is the fact table (64,104 rows, PK = `OrderNumber`).

| Dimension sheet | Join key (Sales Orders → Dimension) | Cardinality |
|---|---|---|
| Customers | `Customer Name Index` → `Customer Index` | N:1 |
| Products | `Product Description Index` → `Index` | N:1 |
| Regions | `Delivery Region Index` → `id` | N:1 |
| State Regions | `state_code` → `State Code` (via Regions) | N:1 |
| 2017 Budgets | `Product Name` (via Products, indirect) | 1:1 per product |

`Warehouse Code` has no dimension sheet — intentionally unmapped and dropped.

---

## Power BI notes (`SALES REPORT.pbix`)

- Data source: the CSV, not the Excel.
- DAX in `Custom Measures` table: `Profit Margin % = DIVIDE(SUM(profit), SUM(revenue), 0) * 100` and `Revenue Per Order = DIVIDE(SUM(revenue), COUNT(order_number))`.
- `order_month_name` must be sorted by `order_month_num` (Sort by Column) or months render alphabetically.
- Canvas backgrounds: PNGs in `Dashboard Backround/` (typo in folder name — preserved for compatibility).

---

## Gradio Interactive Dashboard — COMPLETED

App is fully built and working. Run with `uv run python app.py` → localhost:7860.

### Current state

- **3 tabs**: Overview / Product & Channel / Geography & Customer
- **16 Plotly charts** + 5 KPI cards + 3 rule-based insight panels + 3 LLM buttons
- **Global filter bar**: Year, Channel, US Region, Product (sentinel "All Products")
- **Light theme**: gradient header `#4f8ef7 → #6366f1`, page bg `#f8faff`, white cards
- **38 pytest passing** (`uv run pytest -v`)

### Source-of-truth files

| File | Role | Import rule |
|---|---|---|
| `data.py` | `load_csv()`, `apply_filters()`, `compute_kpis()` | No Gradio import |
| `charts.py` | 16 chart builder functions (pure Plotly) | No Gradio import |
| `insights.py` | Rule-based insights + `llm_recommendation()` (OpenAI) | No Gradio import |
| `theme.py` | `COLORS` dict, `PALETTE` list, `CUSTOM_CSS` string | No Gradio import |
| `app.py` | Only file that imports Gradio — builds Blocks, wires events | Entry point |

### Runtime rules

- Package manager: **`uv`**. Always `uv run xxx` / `uv add xxx`. Never `python3` or `pip`.
- No emoji in code, print, logging, or commit messages.
- `theme=` and `css=` go in `.launch()`, not `gr.Blocks()` (Gradio 6.x).
- Before any commit: `uv run pytest -v` (38 green) + `uv run python -c "from app import build_app; build_app(); print('OK')"`.

### Key conventions

- **Filter semantics**: empty list = no filter on that dimension (`data.py::apply_filters`).
- **Product sentinel**: `"All Products"` option in dropdown — handled in `app.py::_resolve_product_filter`. Never push this sentinel into `data.py`.
- **Gradio state**: `df_full_state` (loaded once at startup), `df_filtered_state` (recomputed on filter change), `filter_dict_state` (fed to insights + LLM prompt).
- **Tab CSS**: tab labels use 3 CSS selectors (`.tab-nav button`, `.tabs > div > button`, `div[class*="tab-nav"] button`) with `color/opacity/visibility: !important` to ensure visibility in Gradio 6.x.

### What was removed / never built

- Explorer tab (PyGWalker) — removed in session 4, not needed.
- CSV upload feature — deferred post-defense.
- HF Spaces deploy — deferred post-defense.
- Cross-filter (click chart → filter other charts) — not supported natively in Gradio.

### Resume reference

Always read `HANDOFF.md` first when starting a new session — it has the latest status, file inventory, and a copy-paste resume prompt.
