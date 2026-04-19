# Regional Sales Dashboard — Implementation Handoff

**Dự án**: Gradio Interactive Dashboard thay thế Power BI cho USA Regional Sales Analysis 2014–2018.
**Bối cảnh**: Đồ án kết thúc môn "Trực quan hoá dữ liệu".
**Last updated**: 2026-04-19 (session 3)

---

## Trạng thái hiện tại

| Bước | Status |
|---|---|
| Exploration & context gathering | done |
| Brainstorming requirements (10 Q&A) | done |
| Design spec | written — `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md` |
| Implementation plan | written — `docs/superpowers/plans/2026-04-18-regional-sales-gradio-implementation.md` |
| Phase 1 — Foundation | done (Task 1-5: deps, data.py+tests, theme.py, app.py skeleton, README) |
| Phase 2 — Tab 1 Overview | done (Task 6-9: compute_kpis, chart builders Tab 1, overview_insight, wire Tab 1) |
| Phase 3 — Tab 2 Product & Channel | done (Task 11-13: 5 chart builders, product_channel_insight, wire Tab 2) |
| Phase 4 — Tab 3 Geo & Customer | done (Task 15-17: 6 chart builders, geo_customer_insight, wire Tab 3 + top/bottom toggle) |
| Phase 5 — LLM integration | done (Task 19-20: summarize_for_llm, llm_recommendation, wire 3 LLM buttons) |
| Phase 6 — Tab 4 Explorer | done (Task 22-23: PyGWalker to_html verified OK, wired on tab select) |
| Phase 7 — Polish & docs | done (Task 24-26: CSS polish, README final, HANDOFF updated) |
| Phase 8 — UI Bug Fix & Design Overhaul | — next (4 bug + full redesign) |
| Phase 9 — (stretch) Upload CSV | — (defer post-defense) |

## Mục tiêu

Xây một Gradio web app với 4 tab (`Overview / Product & Channel / Geography & Customer / Explorer`), global filter bar dùng chung 3 tab chủ đề, Plotly cho chart tương tác, PyGWalker cho tab Explorer, rule-based insights + nút OpenAI LLM cho strategic recommendation. Đọc `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md` để xem chi tiết kiến trúc.

## Success criteria

1. App chạy `uv run python app.py` → Gradio mở browser localhost trong ≤ 3s.
2. Đổi bất kỳ filter nào (Year / Channel / Region / Product) → tất cả chart + rule insight update trong ≤ 1s.
3. 15 phân tích EDA từ notebook hiển thị đầy đủ.
4. Nút LLM trên Tab 1/2/3 trả về khuyến nghị tiếng Việt trong ≤ 10s.
5. Không có `OPENAI_API_KEY` → app vẫn chạy đầy đủ, LLM button báo lỗi rõ ràng (không crash).
6. Tab Explorer PyGWalker hoạt động: kéo-thả dimension/measure → vẽ chart dynamic.
7. Custom CSS áp dụng: header tối, card trắng bo tròn, font đồng bộ Canva background.
8. Filter rỗng (0 dòng) → panel "Không có dữ liệu", không crash.

## Architecture quick-ref

```
Global Filter Bar → gr.State(df_filtered)
                      ↓
        ┌─────────────┴──────────────┐
        ↓             ↓              ↓
     Tab 1        Tab 2          Tab 3     Tab 4 (Explorer, PyGWalker)
  [Overview]  [Product&Chan] [Geo&Cust]
  5 KPI + 4  5 charts +     6 charts +
  charts +   insight +      Top/Bottom
  insight +  LLM btn        toggle +
  LLM btn                   insight +
                            LLM btn
```

**State**:
- `df_full` load 1 lần lúc start.
- `df_filtered` re-compute khi filter đổi.
- `filter_dict` truyền vào rule template + LLM.

**Data source (Phase 1)**: hardcoded `Sales_data(EDA Exported).csv`.

## File inventory (trạng thái file tính đến 2026-04-19)

| File | Status | Ghi chú |
|---|---|---|
| `pyproject.toml` | DONE | deps: gradio 6.12, pygwalker 0.5, openai 2.32, python-dotenv, pytest |
| `uv.lock` | DONE | sync với pyproject |
| `.env.example` | DONE | template OPENAI_API_KEY |
| `.gitignore` | DONE | loại .env, .venv, __pycache__ |
| `data.py` | DONE | `load_csv()` + `apply_filters(df, filters_dict)` — 9 pytest green |
| `theme.py` | DONE | `COLORS` dict + `CUSTOM_CSS` string |
| `app.py` | SKELETON | header + filter bar (Year/Channel/Region/Product with 'All Products' sentinel) + 4 tab rỗng + state wiring. Chưa có chart. |
| `tests/conftest.py` | DONE | fixture `df_full`, `sample_df` |
| `tests/test_data.py` | DONE | 9 tests green |
| `charts.py` | DONE | 16 builders: Tab1 (KPI+4), Tab2 (5), Tab3 (6) — tất cả pure function + empty-df guard |
| `insights.py` | DONE (rule-based) | `overview_insight`, `product_channel_insight`, `geo_customer_insight` — LLM client chưa có |
| `tests/test_charts.py` | DONE | 18 smoke tests green |
| `tests/test_insights.py` | DONE | 4 tests green (incl. geo_customer) |
| `tests/test_kpis.py` | DONE | 4 tests green |
| `README.md` | DONE (v1) | refine thêm screenshot ở Phase 7 |
| `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md` | DONE | design chi tiết, đọc trước khi code |
| `docs/superpowers/plans/2026-04-18-regional-sales-gradio-implementation.md` | DONE | plan chi tiết từng task có code block |
| `CLAUDE.md` (project) | DONE | có section "Gradio app" (mới thêm) |
| `HANDOFF.md` | DONE | file này |

## Ghi chú kỹ thuật quan trọng

### Decisions đã chốt

- **Priority**: interactivity > visual polish > narrative > số chart.
- **Scope**: giữ đủ 15 EDA analyses từ notebook.
- **Phase 1 data**: chỉ hỗ trợ schema cố định của `Sales_data(EDA Exported).csv`. Upload generic CSV là **Phase 2 stretch** — mỗi dataset có format khác nhau nên cần schema validator cẩn thận trước khi mở.
- **LLM**: OpenAI `gpt-4o-mini` (default), override `OPENAI_MODEL` qua env.
- **Cross-filter** (click chart → filter): **không** ở MVP. Gradio không hỗ trợ native.
- **Deploy**: local only. HF Spaces defer post-defense.
- **Tab 4 PyGWalker**: có risk tương thích Gradio mới; fallback = custom mini-explorer dropdown-based.
- **Product filter UX** (update 2026-04-19): dropdown có option sentinel `"All Products"` ở đầu. Default = `["All Products"]`. Khi sentinel có trong selection → không filter theo product. Clear Filters reset về all Year + all Channel + all Region + `["All Products"]`. Sentinel logic nằm trong `app.py::_resolve_product_filter`, KHÔNG trong `data.py::apply_filters` (giữ data.py thuần).

### Gradio 6.x API pitfalls (quan trọng cho session mới)

- `gr.Blocks(theme=..., css=...)` **không còn hoạt động** ở Gradio 6.0+. Phải truyền `theme` + `css` vào `.launch()`:
  ```python
  with gr.Blocks(title="...") as app:   # CHỈ title ở đây
      ...
  app.launch(theme=gr.themes.Soft(), css=CUSTOM_CSS, inbrowser=True)
  ```
- Nếu thấy `UserWarning: The parameters have been moved from the Blocks constructor to the launch() method in Gradio 6.0` → sửa ngay, đừng ignore.
- Plan.md (viết trước 2026-04-18) dùng cú pháp cũ — **CHẾ ĐỘ OPTIONAL: sửa theo Gradio 6.x khi copy code từ plan sang repo**.

### Chart style thống nhất

- `template="plotly_white"`
- Color palette: accent `#6b4eff` (purple/indigo), header bg `#3c3c40`, card bg `#ffffff`.
- Card `border-radius: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12)`.
- Font: Inter / system-ui.

### Risks đang theo dõi

| Risk | Mitigation |
|---|---|
| PyGWalker không tích hợp Gradio | Fallback mini-explorer |
| OpenAI rate limit khi demo | Cache theo hash(filter_dict) |
| 64k rows Plotly chậm | `lru_cache` + downsample scatter |
| CSS vỡ màn hình nhỏ | Test 1440p + 1080p |

## Next task chi tiết (để session mới bắt đầu ngay)

**Phase 8 — UI Bug Fix & Design Overhaul**

Phát hiện sau khi chạy app thật. Thực hiện theo thứ tự ưu tiên:

### Bug CRITICAL (fix trước)

**Bug 1 — Chữ vô hình trong insight & LLM panel** (`theme.py`)
- Triệu chứng: text trong `.insight-panel` và `.llm-output` màu trắng trên nền sáng → không đọc được (bôi chuột mới thấy)
- Root cause: Gradio dark theme set `color: white` toàn cục, CSS của ta không override lại
- Fix: thêm `color: #1a1a1a !important` vào `.insight-panel *` và `.llm-output *`

**Bug 2 — Product dropdown sort sai thứ tự** (`app.py`)
- Triệu chứng: "Product 1" → "Product 10" → "Product 11" → ... → "Product 2" (lexicographic)
- Fix: đổi sort key thành numeric
```python
sorted(product_choices, key=lambda x: int(x.split()[-1]) if x.split()[-1].isdigit() else x)
```

### Chart improvements

**Bug 3 — Histogram "Order Value Distribution" bars sát nhau** (`charts.py::build_aov_histogram`)
- Fix: thêm `bargap=0.08` vào `fig.update_layout()`

**Bug 4 — Thay scatter "Profit Margin % vs Unit Price"** (`charts.py`, `app.py`, `tests/test_charts.py`)
- Vấn đề: unit_price là giá trị rời rạc (30 SKU × giá cố định) → scatter tạo dải dọc, vô nghĩa
- Thay bằng: **"Revenue & Profit by Channel"** — grouped bar chart
  - X: channel (Wholesale / Distributor / Export)
  - 2 bar groups: Revenue (màu accent) vs Profit (màu xanh lá)
  - Tên function mới: `build_revenue_profit_by_channel(df)`
- Cập nhật `render_tab1` và `tab1_outputs` trong `app.py` tương ứng

### Design Overhaul (sau khi fix bug)

**Mục tiêu**: Modern analytics look, tham khảo Grafana / Linear / Retool

**Palette mới** (cập nhật `theme.py::COLORS`):
```python
COLORS = {
    "header_bg":   "#0f1117",   # near-black header
    "page_bg":     "#f1f5f9",   # slate-100
    "card_bg":     "#ffffff",
    "accent":      "#4f8ef7",   # blue (trust, data)
    "accent_alt":  "#22c55e",   # green (profit/positive)
    "warning":     "#f59e0b",   # amber
    "danger":      "#ef4444",   # red
    "text_primary":"#0f172a",   # slate-900
    "text_muted":  "#64748b",   # slate-500
    "border":      "#e2e8f0",   # slate-200
}
```

**Chart color sequence** (colorblind-safe, thay `ACCENT` cứng trong `charts.py`):
```python
PALETTE = ["#4f8ef7","#22c55e","#f59e0b","#a78bfa","#fb923c","#34d399"]
```

**CSS overhaul** (`theme.py::CUSTOM_CSS`) — các điểm chính:
- Page bg: `#f1f5f9` (sáng hơn, ít nhàm hơn `#f6f6f6`)
- Header: `#0f1117` (đậm hơn, chuyên nghiệp hơn `#3c3c40`)
- KPI card: shadow layered `0 1px 3px rgba(0,0,0,0.08), 0 4px 16px rgba(0,0,0,0.06)`
- KPI value: `font-size: 32px` (to hơn, dễ đọc)
- Insight panel: nền `#eff6ff` (xanh nhạt) + border `#2563eb` (xanh đậm) + `color: #0f172a !important`
- LLM output: nền `#fefce8` (vàng nhạt) + border `#d97706` + `color: #0f172a !important`
- Chart container: `border-radius: 12px; overflow: hidden; box-shadow: 0 1px 3px rgba(0,0,0,0.06)`
- Tab selected: dùng accent blue `#4f8ef7` thay vì `#6b4eff`
- Filter bar: subtle `border: 1px solid #e2e8f0`

**Thứ tự thực hiện trong session**:
1. Fix Bug 1 (chữ vô hình) → verify → commit
2. Fix Bug 2 (product sort) → verify → commit
3. Fix Bug 3 (histogram bargap) → verify → commit
4. Thay Bug 4 (scatter → grouped bar) → TDD → verify → commit
5. Design overhaul toàn bộ `theme.py` + `charts.py` palette → verify → commit
6. Cập nhật HANDOFF.md + prompt session tiếp theo

## Commands verify trạng thái (chạy đầu session mới)

```bash
cd "/home/hieu0606sunny/tqhdl/Regional Sales Summary"

# 1. Check git status + branch
git log --oneline -10
git status

# 2. Chạy test đảm bảo baseline green
uv run pytest -v

# 3. Smoke test app skeleton chạy được (Ctrl+C sau khi thấy URL)
uv run python app.py

# 4. Verify import chain
uv run python -c "from app import build_app; build_app(); print('OK')"
```

Kỳ vọng: 37 pytest pass (1 skipped nếu không có OPENAI_API_KEY), app mở localhost:7860, 4 tab đầy đủ chart + insight + LLM button.

## Resume prompt cho session mới (copy-paste)

Đoạn prompt sau đã được cập nhật với trạng thái mới nhất — copy nguyên khối vào chat mới (bất kỳ model nào, Sonnet 4.6 hay Opus đều OK):

````
Tôi tiếp tục dự án **Regional Sales Gradio Dashboard** (đồ án "Trực quan hoá
dữ liệu"). Repo: /home/hieu0606sunny/tqhdl/Regional Sales Summary
(GitHub: https://github.com/Sunny-sunnyy/tqhdl branch main).

## Bối cảnh nhanh

App Gradio đã hoàn tất Phase 1–7 (4 tab, 16 chart, 3 LLM button, PyGWalker).
38 pytest pass. App chạy: `uv run python app.py` → localhost:7860.

Hiện tại cần thực hiện **Phase 8 — UI Bug Fix & Design Overhaul** gồm 4 bug +
full redesign palette/CSS. Chi tiết đầy đủ trong mục "Next task chi tiết"
của HANDOFF.md — ĐỌC KỸ trước khi viết bất cứ dòng code nào.

## Bước 1 — Đọc theo thứ tự (KHÔNG đọc file khác trước):

1. /home/hieu0606sunny/tqhdl/Regional Sales Summary/CLAUDE.md
2. /home/hieu0606sunny/.claude/CLAUDE.md
3. /home/hieu0606sunny/tqhdl/Regional Sales Summary/HANDOFF.md
   → Đọc kỹ mục "Phase 8" trong "Next task chi tiết"

## Bước 2 — Đọc code hiện có TRƯỚC KHI thêm bất cứ thứ gì:

```
theme.py      — COLORS dict + CUSTOM_CSS (sẽ thay toàn bộ)
charts.py     — chart builders (sẽ sửa 2 hàm + đổi palette)
app.py        — filter bar + tab wiring (sửa product sort + thay 1 output)
```

ĐỪNG đọc lại: data.py, insights.py, tests/ (không thay đổi ở Phase 8,
trừ test_charts.py phải cập nhật khi đổi tên hàm scatter → grouped bar).

## Bước 3 — Verify baseline:

```bash
cd "/home/hieu0606sunny/tqhdl/Regional Sales Summary"
uv run pytest -v          # kỳ vọng: 38 passed
uv run python -c "from app import build_app; build_app(); print('OK')"
```

Nếu fail → debug trước theo Debugging Protocol.

## Bước 4 — Thực hiện Phase 8 theo đúng thứ tự:

1. Bug 1: chữ vô hình (theme.py — 2 dòng CSS)
2. Bug 2: product sort numeric (app.py — 1 dòng)
3. Bug 3: histogram bargap (charts.py — 1 dòng)
4. Bug 4: thay scatter → build_revenue_profit_by_channel (TDD)
5. Design overhaul: palette mới + CSS hoàn toàn mới (theme.py + charts.py)

Mỗi bước: sửa → pytest → `build_app()` OK → commit → bước tiếp.
Hỏi tôi muốn **Inline Execution** hay **Subagent-Driven** trước khi bắt đầu.

## Ràng buộc bắt buộc:

- Dùng `uv` (không pip, không python3). `uv run xxx` / `uv add xxx`.
- Không emoji trong code / comment / print / log.
- Gradio 6.x: `theme` và `css` vào `.launch()`, KHÔNG vào `gr.Blocks()`.
- Product filter: sentinel "All Products" trong `_resolve_product_filter` (app.py).
- TDD cho hàm mới `build_revenue_profit_by_channel`: test fail → implement → pass.
- Incremental: mỗi bug xong → confirm → commit → tiếp.
- Giao tiếp: tiếng Việt. Code/comment: English.

Sau khi đọc xong + verify baseline, báo cáo ngắn rồi hỏi execution mode.
````

## Changelog

| Date | Section | Change |
|---|---|---|
| 2026-04-18 | All | Initial handoff — brainstorming xong, spec written, implementation chưa start |
| 2026-04-19 | Trạng thái | Phase 1 Foundation hoàn tất (Task 1-5): deps, data.py + 9 pytest pass, theme.py, app.py skeleton 4 tab chạy HTTP 200, README enrich. Sẵn sàng Phase 2 (Tab 1 Overview). |
| 2026-04-19 | UX | Product dropdown thêm sentinel "All Products" + Clear Filters reset về all-selected thay vì empty. Logic trong `app.py::_resolve_product_filter`. |
| 2026-04-19 | Docs | Mở rộng HANDOFF: file inventory chi tiết, Gradio 6.x pitfalls, next-task chi tiết, verify-baseline commands, resume prompt mới model-agnostic. |
| 2026-04-19 | Phase 2-4 | Hoàn tất: compute_kpis, 16 chart builders (Tab 1-3), 3 rule insights, wire 3 tab vào app.py (filter chain + radio toggles). 35 tests green. |
| 2026-04-19 | Phase 5-7 | Hoàn tất: summarize_for_llm + llm_recommendation, 3 LLM buttons, PyGWalker Explorer, CSS polish, README final. 38 tests green. App sẵn sàng demo. |
| 2026-04-19 | Phase 8 plan | Phát hiện 4 bug khi chạy thật: chữ vô hình insight/LLM, product sort sai, histogram bargap, scatter vô nghĩa. Lên plan design overhaul (palette mới, CSS mới theo Grafana/Linear style). Ghi vào HANDOFF next task. |
