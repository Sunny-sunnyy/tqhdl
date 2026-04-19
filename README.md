# Regional Sales Dashboard

Gradio interactive dashboard cho bộ dữ liệu **USA Regional Sales 2014–2018**.
Đồ án kết thúc môn "Trực quan hoá dữ liệu".

## Nội dung repo

- `EDA_Regional_Sales_Analysis.ipynb` — notebook EDA gốc (15 phân tích).
- `Sales_data(EDA Exported).csv` — dữ liệu đã flatten từ notebook.
- `SALES REPORT.pbix` — báo cáo Power BI (tham khảo cho slide).
- `PPT --- Regional Sales Analysis.pptx` — slide thuyết trình.
- `docs/superpowers/specs/` — design spec.
- `docs/superpowers/plans/` — implementation plan.
- `CLAUDE.md`, `HANDOFF.md` — hướng dẫn context cho session tiếp theo.

## Chạy app (khi đã build xong)

```bash
uv sync
cp .env.example .env   # điền OPENAI_API_KEY
uv run python app.py
```

App mở tại `http://127.0.0.1:7860`.

## Features

- 4 tab: Overview · Product & Channel · Geography & Customer · Explorer
- Global filter bar (Year / Channel / Region / Product) chia sẻ giữa 3 tab chủ đề
- 15 phân tích EDA với chart Plotly tương tác
- PyGWalker kéo-thả ở tab Explorer
- Rule-based insight tự sinh + nút LLM (OpenAI) sinh strategic recommendation
- Custom CSS đồng bộ Canva background của dự án gốc

## Architecture

Xem `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md` cho chi tiết design, `CLAUDE.md` cho codebase guide, `HANDOFF.md` cho trạng thái triển khai.

## Tech stack

Python 3.11 · pandas · Plotly · Gradio · PyGWalker · OpenAI SDK · uv.

## Trạng thái

Xem `HANDOFF.md` để biết phase đang làm.
