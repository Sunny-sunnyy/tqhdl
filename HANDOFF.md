# Regional Sales Dashboard — Implementation Handoff

**Dự án**: Gradio Interactive Dashboard thay thế Power BI cho USA Regional Sales Analysis 2014–2018.
**Bối cảnh**: Đồ án kết thúc môn "Trực quan hoá dữ liệu".
**Last updated**: 2026-04-20 (session 4)

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
| Phase 6 — Tab 4 Explorer | done → **đã xóa** (PyGWalker không cần nữa) |
| Phase 7 — Polish & docs | done (CSS polish, README, HANDOFF) |
| Phase 8 — UI Bug Fix & Design Overhaul | done (4 bug + Grafana-style) |
| Phase 9 — Light theme + Explorer removal | done (session 4) |
| Phase 10 — Data docs + Word export | done (PROJECT_REPORT.docx, sections 3.3–3.4) |
| Phase 11 — (stretch) Upload CSV / HF Spaces | — (defer post-defense) |

## Mục tiêu

Gradio web app với **3 tab** (`Overview / Product & Channel / Geography & Customer`), global filter bar dùng chung, Plotly cho chart tương tác, rule-based insights + nút OpenAI LLM. Tab Explorer (PyGWalker) đã bị xóa. Light theme: gradient header blue-indigo, page bg `#f8faff`, white cards.

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

## File inventory (trạng thái file tính đến 2026-04-20)

| File | Status | Ghi chú |
|---|---|---|
| `pyproject.toml` | DONE | deps: gradio 6.12, python-docx 1.2, openai 2.32, python-dotenv, pytest |
| `uv.lock` | DONE | sync với pyproject |
| `.env.example` | DONE | template OPENAI_API_KEY |
| `.gitignore` | DONE | loại .env, .venv, __pycache__ |
| `data.py` | DONE | `load_csv()` + `apply_filters(df, filters_dict)` — không thay đổi |
| `theme.py` | DONE | Light theme: gradient header, `#f8faff` page bg, tab-nav 3-selector fix |
| `app.py` | DONE | 3 tab (Explorer đã xóa), filter bar, state wiring đầy đủ |
| `tests/conftest.py` | DONE | fixture `df_full`, `sample_df` |
| `tests/test_data.py` | DONE | 9 tests green |
| `charts.py` | DONE | 16 builders — không thay đổi |
| `insights.py` | DONE | rule-based + LLM — không thay đổi |
| `tests/test_charts.py` | DONE | 18 smoke tests green |
| `tests/test_insights.py` | DONE | 7 tests green |
| `tests/test_kpis.py` | DONE | 4 tests green |
| `README.md` | DONE | final |
| `PROJECT_REPORT.md` | DONE | báo cáo đầy đủ, có sections 3.3–3.4 mô tả dữ liệu chi tiết |
| `PROJECT_REPORT.docx` | DONE | Word version của báo cáo (85KB, ~40 trang) |
| `CLAUDE.md` (project) | DONE | có section "Gradio app" |
| `HANDOFF.md` | DONE | file này |

## Ghi chú kỹ thuật quan trọng

### Decisions đã chốt

- **Priority**: interactivity > visual polish > narrative > số chart.
- **Scope**: giữ đủ 15 EDA analyses từ notebook.
- **Phase 1 data**: chỉ hỗ trợ schema cố định của `Sales_data(EDA Exported).csv`. Upload generic CSV là **Phase 2 stretch** — mỗi dataset có format khác nhau nên cần schema validator cẩn thận trước khi mở.
- **LLM**: OpenAI `gpt-4o-mini` (default), override `OPENAI_MODEL` qua env.
- **Cross-filter** (click chart → filter): **không** ở MVP. Gradio không hỗ trợ native.
- **Deploy**: local only. HF Spaces defer post-defense.
- **Tab Explorer (PyGWalker)**: đã xóa hoàn toàn khỏi app. App còn 3 tab.
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
- PALETTE: `["#4f8ef7","#10b981","#f59e0b","#6366f1","#fb923c","#34d399"]`
- Header: gradient `#4f8ef7 → #6366f1` (blue-indigo), **không dùng màu tối**.
- Page bg: `#f8faff`. Card bg: `#ffffff`. Card `border-radius: 16px`.
- Font: Inter / system-ui.

### Risks đang theo dõi

| Risk | Mitigation |
|---|---|
| OpenAI rate limit khi demo | Không có API key → LLM button báo lỗi rõ, app không crash |
| 64k rows Plotly chậm | `lru_cache` + downsample scatter |
| Tab CSS không hiển thị (Gradio 6.x) | Đã fix: 3-selector rule + `color/opacity/visibility !important` |

## Trạng thái hiện tại — App sẵn sàng demo

**Không còn task nào pending.** App hoàn chỉnh, 38 tests green, light theme đẹp.

Nếu session mới phát hiện bug khi chạy thật → debug theo Debugging Protocol trong CLAUDE.md.

## Commands verify trạng thái (chạy đầu session mới)

```bash
cd "/home/hieu0606sunny/tqhdl/Regional Sales Summary"
git log --oneline -5
uv run pytest -v
uv run python -c "from app import build_app; build_app(); print('OK')"
```

Kỳ vọng: **38 passed**, build_app() in `OK`, app mở localhost:7860, **3 tab** đầy đủ chart + insight + LLM button.

## Resume prompt cho session mới (copy-paste)

Đoạn prompt sau đã cập nhật với trạng thái mới nhất — copy nguyên khối vào chat mới:

````
Tôi tiếp tục dự án **Regional Sales Gradio Dashboard** (đồ án "Trực quan hoá
dữ liệu"). Repo: /home/hieu0606sunny/tqhdl/Regional Sales Summary
(GitHub: https://github.com/Sunny-sunnyy/tqhdl branch main).

## Bối cảnh nhanh

App Gradio đã hoàn tất Phase 1–10:
- **3 tab**: Overview / Product & Channel / Geography & Customer (Explorer đã xóa)
- 16 chart (Plotly), 3 LLM button (OpenAI gpt-4o-mini)
- Light theme: gradient header blue-indigo (#4f8ef7→#6366f1), page bg #f8faff
- Tab CSS fix: tất cả tab label hiển thị ngay, không cần hover
- 38 pytest pass. App chạy: `uv run python app.py` → localhost:7860
- Báo cáo: PROJECT_REPORT.md + PROJECT_REPORT.docx (Word, ~40 trang)

Không còn task pending. Nếu phát hiện bug mới khi chạy thật thì báo cáo.

## Bước 1 — Đọc theo thứ tự (KHÔNG đọc file khác trước):

1. /home/hieu0606sunny/tqhdl/Regional Sales Summary/CLAUDE.md
2. /home/hieu0606sunny/.claude/CLAUDE.md
3. /home/hieu0606sunny/tqhdl/Regional Sales Summary/HANDOFF.md

## Bước 2 — Đọc code hiện có TRƯỚC KHI thêm bất cứ thứ gì:

```
theme.py    — light theme: gradient header, #f8faff bg, tab-nav 3-selector
charts.py   — 16 builders (Tab 1-3), pure Plotly
app.py      — filter bar + 3 tab + state wiring (Explorer đã xóa)
data.py     — load_csv() + apply_filters() (không thay đổi)
insights.py — rule-based + LLM (không thay đổi)
```

## Bước 3 — Verify baseline:

```bash
cd "/home/hieu0606sunny/tqhdl/Regional Sales Summary"
uv run pytest -v          # kỳ vọng: 38 passed
uv run python -c "from app import build_app; build_app(); print('OK')"
```

Nếu fail → debug trước theo Debugging Protocol.

## Ràng buộc bắt buộc:

- Dùng `uv` (không pip, không python3). `uv run xxx` / `uv add xxx`.
- Không emoji trong code / comment / print / log.
- Gradio 6.x: `theme` và `css` vào `.launch()`, KHÔNG vào `gr.Blocks()`.
- Product filter: sentinel "All Products" trong `_resolve_product_filter` (app.py).
- Incremental: mỗi thay đổi xong → pytest → build_app() → commit → tiếp.
- Giao tiếp: tiếng Việt. Code/comment: English.
- **Không dùng màu tối** trong CSS — light theme đã chốt.

Sau khi đọc xong + verify baseline, báo cáo ngắn trạng thái app.
````

## Changelog

| Date | Session | Change |
|---|---|---|
| 2026-04-18 | 1 | Initial handoff — brainstorming xong, spec + plan written |
| 2026-04-19 | 2 | Phase 1-5: Foundation, 3 tab, 16 charts, 3 rule insights, LLM buttons, PyGWalker. 38 tests green. |
| 2026-04-19 | 3 | Phase 6-8: PyGWalker Explorer, CSS polish, README. Fix 4 bugs (text color, product sort, bargap, scatter→bar). Design overhaul Grafana-style. |
| 2026-04-20 | 4 | Phase 9-10: Tab CSS visibility fix (3-selector rule). Light theme redesign (gradient header, #f8faff bg). Explorer tab xóa. PROJECT_REPORT sections 3.3–3.4 (data dictionary chi tiết). PROJECT_REPORT.docx export. 38 tests green. |
