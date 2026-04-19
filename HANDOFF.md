# Regional Sales Dashboard — Implementation Handoff

**Dự án**: Gradio Interactive Dashboard thay thế Power BI cho USA Regional Sales Analysis 2014–2018.
**Bối cảnh**: Đồ án kết thúc môn "Trực quan hoá dữ liệu".
**Last updated**: 2026-04-19

---

## Trạng thái hiện tại

| Bước | Status |
|---|---|
| Exploration & context gathering | done |
| Brainstorming requirements (10 Q&A) | done |
| Design spec | written — `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md` |
| Implementation plan | written — `docs/superpowers/plans/2026-04-18-regional-sales-gradio-implementation.md` |
| Phase 1 — Foundation | done (Task 1-5: deps, data.py+tests, theme.py, app.py skeleton, README) |
| Phase 2 — Tab 1 Overview | — next |
| Phase 3 — Tab 2 Product & Channel | — |
| Phase 4 — Tab 3 Geo & Customer | — |
| Phase 5 — LLM integration | — |
| Phase 6 — Tab 4 Explorer | — |
| Phase 7 — Polish & docs | — |
| Phase 8 — (stretch) Upload CSV | — |

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
| `charts.py` | TODO | Phase 2-4: 16 chart builder functions (pure, trả `plotly.graph_objects.Figure`) |
| `insights.py` | TODO | Phase 2+: rule templates + OpenAI client wrapper |
| `tests/test_charts.py` | TODO | smoke test chart builders |
| `tests/test_insights.py` | TODO | Phase 2, 5 |
| `tests/test_kpis.py` | TODO | Task 6 |
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

**Phase 2 — Task 6: KPI aggregation functions (TDD)**

- File: modify `data.py` (thêm `compute_kpis`), create `tests/test_kpis.py`.
- Flow chuẩn TDD: viết test fail → implement → test pass → commit.
- Code mẫu có sẵn trong `docs/superpowers/plans/2026-04-18-regional-sales-gradio-implementation.md` ở phần **Task 6** (dòng ~550). Copy code, chạy, đừng tự sáng tác lại.
- KPIs cần tính: `total_revenue`, `total_profit`, `profit_margin_pct`, `total_orders`, `revenue_per_order`.
- Sau Task 6: tiếp Task 7 (build_kpi_cards UI), Task 8 (4 chart Overview), Task 9 (rule insight), Task 10 (wire vào Tab 1).

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

Kỳ vọng: 9 pytest pass, app mở localhost:7860, header đen + filter bar + 4 tab rỗng.

## Resume prompt cho session mới (copy-paste)

Đoạn prompt sau đã được cập nhật với trạng thái mới nhất — copy nguyên khối vào chat mới (bất kỳ model nào, Sonnet 4.6 hay Opus đều OK):

````
Tôi tiếp tục dự án **Regional Sales Gradio Dashboard** (đồ án "Trực quan hoá
dữ liệu"). Repo: /home/hieu0606sunny/tqhdl/Regional Sales Summary
(GitHub: https://github.com/Sunny-sunnyy/tqhdl branch main).

## Bước 1 — Đọc theo thứ tự (KHÔNG đọc file khác trước):

1. /home/hieu0606sunny/tqhdl/Regional Sales Summary/CLAUDE.md        (project guide + Gradio section)
2. /home/hieu0606sunny/.claude/CLAUDE.md                             (global rules)
3. /home/hieu0606sunny/tqhdl/Regional Sales Summary/HANDOFF.md       (trạng thái + pitfalls + next task)
4. /home/hieu0606sunny/tqhdl/Regional Sales Summary/docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md
5. /home/hieu0606sunny/tqhdl/Regional Sales Summary/docs/superpowers/plans/2026-04-18-regional-sales-gradio-implementation.md

## Bước 2 — Verify baseline:

Chạy 4 lệnh trong mục "Commands verify trạng thái" của HANDOFF.md.
Nếu 9 pytest pass + app skeleton chạy được → OK sang Bước 3.
Nếu fail → debug trước, theo Debugging Protocol của global CLAUDE.md.

## Bước 3 — Đọc code đã có trước khi viết:

ĐÃ TỒN TẠI (đọc hết trước khi thêm code): app.py, data.py, theme.py,
tests/conftest.py, tests/test_data.py. ĐỪNG viết lại những file này.

## Bước 4 — Báo cáo và hỏi:

Nói ngắn gọn:
- Phase 1 đã xong (theo HANDOFF.md).
- Next task: Phase 2 Task 6 (compute_kpis TDD).
- Hỏi tôi muốn **Subagent-Driven** (dispatch subagent/task) hay
  **Inline Execution** (chạy tuần tự).

## Ràng buộc bắt buộc:

- Dùng `uv` (không pip, không python3). `uv run xxx` / `uv add xxx`.
- Không emoji trong code / comment / print / log.
- Gradio 6.x API: `theme` và `css` truyền vào `.launch()`, KHÔNG vào `gr.Blocks()`.
  Xem mục "Gradio 6.x API pitfalls" trong HANDOFF.md.
- Product filter: có sentinel "All Products". Xem `_resolve_product_filter` trong app.py.
- Incremental — mỗi task xong → dừng → chờ tôi confirm → commit → task tiếp.
- Tuân thủ CLAUDE.md global rules: 3-Solution Rule, Debugging Protocol, TDD, Stop & Ask.
- Giao tiếp: tiếng Việt. Code / comment: English.

Sau khi đọc xong + verify baseline, bắt đầu Bước 4.
````

## Changelog

| Date | Section | Change |
|---|---|---|
| 2026-04-18 | All | Initial handoff — brainstorming xong, spec written, implementation chưa start |
| 2026-04-19 | Trạng thái | Phase 1 Foundation hoàn tất (Task 1-5): deps, data.py + 9 pytest pass, theme.py, app.py skeleton 4 tab chạy HTTP 200, README enrich. Sẵn sàng Phase 2 (Tab 1 Overview). |
| 2026-04-19 | UX | Product dropdown thêm sentinel "All Products" + Clear Filters reset về all-selected thay vì empty. Logic trong `app.py::_resolve_product_filter`. |
| 2026-04-19 | Docs | Mở rộng HANDOFF: file inventory chi tiết, Gradio 6.x pitfalls, next-task chi tiết, verify-baseline commands, resume prompt mới model-agnostic. |
