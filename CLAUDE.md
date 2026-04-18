# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository nature

This is a **data analytics portfolio project** (USA Regional Sales Analysis, 2014–2018), not a software codebase. There is no package manager, build system, or test suite. Artifacts are a Jupyter notebook, an Excel source, an exported CSV, a Power BI `.pbix`, and a `.pptx`. Documentation (`Summary.txt`, `USA_Regional_Sales_Analysis_Project_Documentation.txt`) is in Vietnamese; code and comments in the notebook are in English.

## Data pipeline

The artifacts form a strict linear pipeline — breaking any step breaks downstream:

```
Regional Sales Dataset.xlsx        (source: 6 sheets)
    └─► EDA_Regional_Sales_Analysis.ipynb   (cleans, merges, feature-engineers)
            └─► Sales_data(EDA Exported).csv   (64,104 rows × 21 cols)
                    └─► SALES REPORT.pbix     (Power BI dashboard, 3 pages)
                            └─► PPT --- Regional Sales Analysis.pptx
```

The CSV is both the notebook's output and Power BI's input — if you rename/move it, update both the notebook's `df.to_csv(...)` call (Cell 75) and the Power BI data source.

## Notebook architecture (`EDA_Regional_Sales_Analysis.ipynb`)

80 cells. Written for **Google Colab** — Cell 10 contains `from google.colab import drive; drive.mount(...)` and an absolute Drive path. When running locally, replace these with a local `file_path` before running.

Logical phases by cell range:
- Cells 8–10: imports (pandas, numpy, matplotlib, seaborn) + `pd.read_excel(file_path, sheet_name=None)` to load all 6 sheets into a dict.
- Cells 11–18: profiling (nulls, dtypes, duplicates) + fix for `State Regions` sheet whose first row contains the real headers.
- Cell 19: **the merge pipeline** — 5 consecutive `left` joins with `Sales Orders` as the fact table. Do not change the join type; it preserves all 64,104 fact rows.
- Cells 20–25: column pruning, rename to `snake_case`, null out budget for non-2017 years.
- Cell 26: feature engineering — `total_cost`, `profit`, `profit_margin_pct`, plus the paired `order_month_name` + `order_month_num` (both are needed: the name renders on charts, the number drives Power BI's "Sort by Column").
- Cell 32: filters out 2018 (only Jan–Feb present → would skew monthly aggregates when collapsing across years).
- Cells 33–74: 15 EDA analyses (temporal, univariate, bivariate, multivariate, geospatial).
- Cell 75: exports the CSV consumed by Power BI.

## Data model (ERD)

`Sales Orders` is the fact table. Merge keys used in Cell 19:

| Dimension | Join condition |
|---|---|
| Customers | `Customer Name Index` ↔ `Customer Index` |
| Products | `Product Description Index` ↔ `Index` |
| Regions | `Delivery Region Index` ↔ `id` |
| State Regions | `state_code` ↔ `State Code` |
| 2017 Budgets | `Product Name` (via Products, not directly to Sales Orders) |

`Warehouse Code` in Sales Orders has no matching dimension sheet and is intentionally unmapped.

## Power BI notes (`SALES REPORT.pbix`)

- Data source is the CSV, not the Excel. Regenerate the CSV before refreshing.
- DAX measures live in a `Custom Measures` table: `Profit Margin % = DIVIDE(SUM(profit), SUM(revenue), 0) * 100` and `Revenue Per Order = DIVIDE(SUM(revenue), COUNT(order_number))`.
- `order_month_name` must be sorted by `order_month_num` (Sort by Column) or months render alphabetically.
- Canvas backgrounds are PNGs in `Dashboard Backround/` (note the typo — preserved for compatibility).

## Common tasks

- **Rerun the pipeline**: edit `file_path` in Cell 10, run all cells, confirm Cell 75 writes the CSV, then refresh Power BI.
- **Add a new feature column**: add it in Cell 26 (so it flows to the CSV), then add it as a field/measure in Power BI.
- **Change cleaning logic**: changes in Cells 15–24 cascade through the merge (Cell 19) and all downstream EDA — rerun the whole notebook, don't run cells piecemeal.
