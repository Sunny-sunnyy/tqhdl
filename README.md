# USA Regional Sales — Interactive Gradio Dashboard

Đồ án môn **Trực quan hoá dữ liệu** — Gradio web app thay thế Power BI, tái hiện
15 phân tích EDA từ notebook, 5 KPI card, tab Explorer tự do, và nút AI sinh
khuyến nghị chiến lược tiếng Việt.

Dataset: USA Regional Sales 2014–2018 (64,104 đơn hàng × 21 cột).

## Tính năng

- **4 tab**: Overview · Product & Channel · Geography & Customer · Explorer
- **Global filter** (Year · Channel · Region · Product) chia sẻ 3 tab chủ đề
- **5 KPI card**: Total Revenue · Profit · Margin % · Orders · Revenue/Order
- **16 Plotly chart**: line, bar, pie, histogram, scatter, boxplot, choropleth, bubble, heatmap
- **Toggle**: Monthly Revenue time-series ↔ seasonal · Top 10 ↔ Bottom 10 customers
- **Rule-based insight** tự động sinh theo filter hiện tại (3 tab)
- **AI Strategic Recommendation**: nút trên mỗi tab gọi OpenAI GPT sinh 3–5 bullet tiếng Việt
- **Explorer tab**: PyGWalker 0.5.x kéo-thả dimension/measure tự do
- **Empty-filter guard**: mọi chart hiển thị thông báo thay vì crash khi 0 dòng

## Cài đặt

```bash
uv sync                    # install deps từ pyproject.toml
cp .env.example .env       # tạo .env
# Edit .env: OPENAI_API_KEY=sk-...  (tùy chọn, bỏ trống vẫn chạy)
```

## Chạy

```bash
uv run python app.py
# -> http://127.0.0.1:7860
```

## Test

```bash
uv run pytest -v
# 37 passed, 1 skipped (LLM test skip nếu không có OPENAI_API_KEY)
```

## Architecture

| Module | Trách nhiệm |
|---|---|
| `app.py` | Gradio Blocks UI, event handler, state management |
| `data.py` | Load CSV, apply filters, compute KPIs, summarize cho LLM |
| `charts.py` | 16 chart builders (pure functions, trả `go.Figure`) |
| `insights.py` | Rule-based templates + OpenAI client wrapper |
| `theme.py` | CSS + color palette |
| `tests/` | 37 pytest: data, KPIs, charts (smoke), insights |

## Pipeline dữ liệu

```
Regional Sales Dataset.xlsx
    -> EDA_Regional_Sales_Analysis.ipynb
        -> Sales_data(EDA Exported).csv   <- app.py đọc file này
```

## Tech stack

Python 3.12 · pandas · Plotly · Gradio 6.x · PyGWalker 0.5 · OpenAI SDK · uv

## Nội dung repo

- `EDA_Regional_Sales_Analysis.ipynb` — notebook EDA gốc (15 phân tích)
- `Sales_data(EDA Exported).csv` — dữ liệu đã flatten (64,104 rows)
- `SALES REPORT.pbix` — báo cáo Power BI (tham khảo slide)
- `PPT --- Regional Sales Analysis.pptx` — slide thuyết trình
- `CLAUDE.md`, `HANDOFF.md` — context guide cho session tiếp theo
- `docs/superpowers/specs/` — design spec
- `docs/superpowers/plans/` — implementation plan chi tiết
