# Regional Sales Dashboard — Implementation Handoff

**Dự án**: Gradio Interactive Dashboard thay thế Power BI cho USA Regional Sales Analysis 2014–2018.
**Bối cảnh**: Đồ án kết thúc môn "Trực quan hoá dữ liệu".
**Last updated**: 2026-04-18

---

## Trạng thái hiện tại

| Bước | Status |
|---|---|
| Exploration & context gathering | ✓ done |
| Brainstorming requirements (10 Q&A) | ✓ done |
| Design spec | ✓ written — `docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md` |
| `plan.md` (implementation plan) | — chưa sinh (bước tiếp theo) |
| Phase 1 — Foundation | — |
| Phase 2 — Tab 1 Overview | — |
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

## File map

```
app.py              # Gradio Blocks UI + callbacks
data.py             # load_csv, apply_filters, summarize_for_llm
charts.py           # 15+ chart builders (pure functions)
insights.py         # rule templates + OpenAI client
theme.py            # custom CSS string
.env                # OPENAI_API_KEY (git-ignored)
.env.example        # template
pyproject.toml      # uv deps (có sẵn — cần thêm gradio, pygwalker, openai, python-dotenv)
docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md   # design chi tiết
plan.md             # implementation plan (sinh từ writing-plans skill)
HANDOFF.md          # file này
CLAUDE.md           # codebase guide cho Claude
README.md           # hướng dẫn chạy app
```

## Ghi chú kỹ thuật quan trọng

### Decisions đã chốt

- **Priority**: interactivity > visual polish > narrative > số chart.
- **Scope**: giữ đủ 15 EDA analyses từ notebook.
- **Phase 1 data**: chỉ hỗ trợ schema cố định của `Sales_data(EDA Exported).csv`. Upload generic CSV là **Phase 2 stretch** — mỗi dataset có format khác nhau nên cần schema validator cẩn thận trước khi mở.
- **LLM**: OpenAI `gpt-4o-mini` (default), override `OPENAI_MODEL` qua env.
- **Cross-filter** (click chart → filter): **không** ở MVP. Gradio không hỗ trợ native.
- **Deploy**: local only. HF Spaces defer post-defense.
- **Tab 4 PyGWalker**: có risk tương thích Gradio mới; fallback = custom mini-explorer dropdown-based.

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

## Resume prompt cho session mới

Khi mở chat mới (vì context quá dài, hoặc tiếp tục ngày khác), gửi đoạn này:

```
Tôi đang tiếp tục dự án Regional Sales Gradio Dashboard (đồ án Trực quan hoá
dữ liệu). Hãy đọc theo thứ tự:

1. /home/hieu0606sunny/tqhdl/Regional Sales Summary/CLAUDE.md
2. /home/hieu0606sunny/tqhdl/Regional Sales Summary/docs/superpowers/specs/2026-04-18-regional-sales-gradio-design.md
3. /home/hieu0606sunny/tqhdl/Regional Sales Summary/HANDOFF.md
4. /home/hieu0606sunny/tqhdl/Regional Sales Summary/plan.md  (nếu đã có)

Sau đó kiểm tra mục "Trạng thái hiện tại" và "Tiến độ theo phase" trong
HANDOFF.md, xác định phase đang làm dở, và hỏi tôi muốn tiếp tục từ đâu.

Nếu có code đã viết trong app.py, data.py, charts.py, insights.py, theme.py
thì đọc hết trước khi bắt đầu — đừng viết lại. Tuân thủ CLAUDE.md global
rules của tôi (uv, incremental, no placeholders, no emoji).
```

## Changelog

| Date | Section | Change |
|---|---|---|
| 2026-04-18 | All | Initial handoff — brainstorming xong, spec written, implementation chưa start |
