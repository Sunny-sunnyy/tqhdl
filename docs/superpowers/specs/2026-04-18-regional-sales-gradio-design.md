# USA Regional Sales — Interactive Gradio Dashboard

**Status**: Draft — chờ user review
**Date**: 2026-04-18
**Context**: Đồ án kết thúc môn "Trực quan hoá dữ liệu" (bao gồm phân tích dữ liệu)

---

## 1. Bối cảnh & Mục tiêu

Dự án gốc đã hoàn thành pipeline Excel → Notebook EDA → CSV sạch → Power BI dashboard 3 trang. Bây giờ xây một **Gradio web app** thay thế Power BI, thoả mãn đầu bài của giảng viên: *"một app thể hiện được dashboard, người dùng có thể tương tác với dashboard đó"*.

**Mục tiêu chính** (ưu tiên giảm dần):
1. **Interactivity** — filter mượt, re-render nhanh, Explorer tab cho phép kéo-thả khám phá.
2. **Visual polish** — custom CSS match style Canva background, layout chỉn chu.
3. **Narrative & insight** — mỗi tab có insight rule-based tự sinh theo filter + nút LLM sinh khuyến nghị chiến lược.
4. **Quantity** — giữ đủ 15 phân tích EDA từ notebook.

Power BI `.pbix` chỉ là tham khảo (dùng cho slide PPT), **không bắt buộc copy 1:1**.

## 2. Non-goals

- Không clone 100% Power BI (bookmark, drill-through thật sự không khả thi trong Gradio).
- Không làm cross-filter click-chart-to-filter ở MVP (Gradio không hỗ trợ native, cần custom JS — defer).
- Không hỗ trợ multi-user auth, database persistence, scheduled refresh.
- Không deploy HF Spaces ở Phase 1 (local demo là chính).
- **Không** build upload CSV generic ở Phase 1 — schema cố định theo `Sales_data(EDA Exported).csv` (xem Phase 2 stretch).

## 3. Users & Use cases

**Primary user**: Giảng viên môn Trực quan hoá dữ liệu — demo 10–15 phút trên máy sinh viên.

**Use cases**:
1. Giảng viên mở app → thấy dashboard Overview ngay (default filter = tất cả).
2. Sinh viên đổi filter (vd. Year=2017, Channel=Export) → 3 tab chủ đề cùng cập nhật; dẫn qua từng tab kể chuyện.
3. Sinh viên bấm nút "Strategic Recommendation (AI)" → LLM sinh 3–5 khuyến nghị dựa trên filter hiện tại.
4. Sinh viên mở tab Explorer → kéo-thả dimension/measure trong PyGWalker để trả lời câu hỏi ad-hoc của giảng viên.

## 4. Kiến trúc tổng quan

```
┌──────────────────────────────────────────────────────────────┐
│ Header (dark): "USA Regional Sales Dashboard"                │
├──────────────────────────────────────────────────────────────┤
│ Global Filter Bar                                            │
│ [Year ✓✓✓✓] [Channel ✓✓✓] [Region ✓✓✓✓] [Product ▾] [Clear] │
├──────────────────────────────────────────────────────────────┤
│ Tabs: Overview │ Product & Channel │ Geography & Customer │  │
│        Explorer                                              │
├──────────────────────────────────────────────────────────────┤
│                     Tab content area                         │
└──────────────────────────────────────────────────────────────┘
```

**State model**:
- `df_full: gr.State` — DataFrame gốc load 1 lần lúc start (64,104 rows × 21 cols).
- `df_filtered: gr.State` — DataFrame đã áp filter hiện tại. Tính lại 1 lần khi filter đổi, tất cả chart callback đọc từ đây.
- `filter_dict: gr.State` — dict `{year, channel, region, product}`; truyền vào rule template + LLM prompt.

**Data flow khi filter đổi**:
```
filter widget change
  → compute_filter_state(df_full, filters) → (df_filtered, filter_dict)
       → 15+ chart builders re-render từ df_filtered
       → 3 rule-based insight texts re-compute
  (LLM button KHÔNG tự trigger — chỉ gọi khi user bấm)
```

**Performance**: 64k rows filter + 6–7 chart Plotly/tab ≈ 300–500ms. Chấp nhận được. Fallback: `functools.lru_cache` trên tuple filter.

## 5. Hợp đồng dữ liệu

**Source**: `Sales_data(EDA Exported).csv` (21 cols, 64,104 rows, sản phẩm của EDA notebook).

**Columns dùng trong app**:

| Column | Type | Dùng cho |
|---|---|---|
| `order_number` | str | count unique orders |
| `order_date` | datetime | filter Year, line charts |
| `customer_name` | str | top/bottom customers, bubble segmentation |
| `channel` | str | filter, pie, bar margin |
| `product_name` | str | filter, top N bar, boxplot |
| `quantity` | int | correlation, explorer |
| `unit_price` | float | scatter, boxplot |
| `revenue` | float | KPI, sum aggregates |
| `cost` | float | correlation |
| `state` | str (2-letter) | choropleth |
| `state_name` | str | top states bar |
| `us_region` | str | filter, region bar |
| `total_cost`, `profit`, `profit_margin_pct` | float | KPI, scatter, bar |
| `order_month_name`, `order_month_num`, `order_month` | str/int | monthly trend lines |

`budget`, `lat`, `lon` — có sẵn nhưng **không dùng ở MVP**; giữ cho Phase 2.

Schema cứng ở Phase 1. Phase 2 mở upload → cần `data.validate_schema(df)` raise error nếu thiếu cột.

## 6. Thiết kế component

### 6.1 UI Layout chi tiết

**Tab 1 — Executive Overview**
- Row 1: 5 KPI card (`gr.HTML` custom để có border radius + color accent):
  - Total Revenue, Total Profit, Profit Margin %, Total Orders, Revenue Per Order
- Row 2 (2 col): Monthly Revenue (line) + `gr.Radio[Time series | Seasonal pattern]` toggle | Monthly Profit (line)
- Row 3 (2 col): AOV Histogram | Unit Price vs Margin scatter
- Row 4: `gr.Markdown` — rule-based insight
- Row 5: `gr.Button` "Sinh Strategic Recommendation (AI)" → `gr.Markdown` output

**Tab 2 — Product & Channel**
- Row 1 (2 col): Top 10 Products by Revenue | Top 10 Products by Avg Profit
- Row 2 (2 col): Sales by Channel (pie) | Avg Profit Margin by Channel (bar)
- Row 3: Unit Price Distribution per Product (boxplot, full width)
- Row 4 + 5: insight + LLM button

**Tab 3 — Geography & Customer**
- Row 1 (2 col): Sales by US Region (bar) | Choropleth Map
- Row 2: Top 10 States Revenue + Orders (dual bars, full width)
- Row 3 (2 col): `gr.Radio["Top 10","Bottom 10"]` → Customer bar | Customer Segmentation (bubble)
- Row 4 (2 col): Correlation Heatmap | insight markdown
- Row 5: LLM button

**Tab 4 — Data Explorer**
- Full-width PyGWalker component, input = `df_filtered`.
- Note: PyGWalker có filter riêng; global filter chỉ là starting point. User có thể reset trong PyGWalker.

### 6.2 Filter system

| Widget | Type | Values | Default |
|---|---|---|---|
| Year | `gr.CheckboxGroup` | 2014, 2015, 2016, 2017, 2018 | tất cả |
| Channel | `gr.CheckboxGroup` | Wholesale, Distributor, Export | tất cả |
| Region | `gr.CheckboxGroup` | West, South, Midwest, Northeast | tất cả |
| Product | `gr.Dropdown(multiselect=True)` | 30 products | `[]` (= tất cả) |
| Clear | `gr.Button` | — | — |

**Semantics**: rỗng = không lọc. `[]` (list rỗng) hay không chọn gì = giữ tất cả.

**Empty-filter guard**: nếu `df_filtered.empty` → mọi chart builder return 1 Plotly figure annotation "Không có dữ liệu với filter hiện tại"; KPI card show `—`.

### 6.3 State management

Gradio `gr.Blocks` + `.change()` event. Filter change event chain:

```python
filter_change_chain = [year, channel, region, product]
for widget in filter_change_chain:
    widget.change(
        fn=update_filters,
        inputs=[df_full, year, channel, region, product],
        outputs=[df_filtered, filter_dict]
    ).then(
        fn=render_all_tabs,
        inputs=[df_filtered, filter_dict],
        outputs=[*tab1_outputs, *tab2_outputs, *tab3_outputs]
    )
```

Explorer tab không render lại khi filter đổi (chi phí PyGWalker rebuild cao) — user chuyển tab → app refresh PyGWalker (on tab change event).

### 6.4 Chart builders — `charts.py`

Mỗi chart = 1 function `build_<name>(df, filters) -> plotly.graph_objects.Figure`. Pure function, không side effect, không đọc global state.

| # | Function | Chart type | Tab |
|---|---|---|---|
| 1 | `build_kpi_cards(df)` | 5 HTML cards (returns markdown/HTML) | 1 |
| 2 | `build_monthly_revenue(df, mode)` | px.line — `mode="timeseries"` theo YYYY-MM (analysis #1) / `mode="seasonal"` theo `order_month_name` trung bình các năm (analysis #2). Có `gr.Radio` toggle trên UI. | 1 |
| 3 | `build_monthly_profit(df)` | px.line — parity với Power BI Monthly Profit | 1 |
| 4 | `build_aov_histogram(df)` | px.histogram (50 bins) | 1 |
| 5 | `build_price_margin_scatter(df)` | px.scatter (alpha) | 1 |
| 6 | `build_top_products_revenue(df, n=10)` | px.bar horizontal | 2 |
| 7 | `build_top_products_profit(df, n=10)` | px.bar horizontal | 2 |
| 8 | `build_channel_pie(df)` | px.pie | 2 |
| 9 | `build_margin_by_channel(df)` | px.bar | 2 |
| 10 | `build_price_boxplot(df)` | px.box | 2 |
| 11 | `build_region_bar(df)` | px.bar horizontal | 3 |
| 12 | `build_state_choropleth(df)` | px.choropleth (locationmode='USA-states') | 3 |
| 13 | `build_states_dual_bar(df)` | go.Figure 2 traces | 3 |
| 14 | `build_customer_bar(df, mode="top")` | px.bar horizontal (Top/Bottom) | 3 |
| 15 | `build_customer_bubble(df)` | px.scatter (size=orders) | 3 |
| 16 | `build_correlation_heatmap(df)` | px.imshow | 3 |

Chart style thống nhất: `template="plotly_white"`, color palette theo Canva accent (purple/indigo), margin compact, title ngắn gọn.

### 6.5 Insight engine — `insights.py`

**Rule-based** (tự động khi filter đổi):

```python
def overview_insight(df: pd.DataFrame, filters: dict) -> str:
    """Return 3-4 bullets markdown."""
    # - tổng revenue, profit, orders, margin %
    # - tháng peak revenue + giá trị
    # - so sánh với filter (if year=specific, ...)

def product_channel_insight(df, filters) -> str: ...
def geo_customer_insight(df, filters) -> str: ...
```

Format output Markdown, dùng bold cho số, đơn vị `$1.24B / $50M / $120K` tuỳ scale.

**LLM Strategic Recommendation** (`insights.py`):

```python
def llm_recommendation(
    df_filtered: pd.DataFrame,
    filters: dict,
    focus: Literal["overview","product_channel","geo_customer"],
) -> str:
    """Gọi OpenAI, trả về Markdown 3-5 bullets."""
```

- Provider: OpenAI. Model default `gpt-4o-mini`, override qua env `OPENAI_MODEL`.
- Key nạp từ `.env` qua `python-dotenv`.
- Summary gửi LLM (tránh gửi toàn bộ dataframe):
  ```json
  {
    "filters": {...},
    "kpis": {"revenue": 1234.5, "profit": 456.7, "margin_pct": 37.0, "orders": 5432},
    "top_products": [{"name": "Product 26", "rev": 118.0}, ...],
    "top_channels": [...],
    "top_regions": [...],
    "peak_month": "May",
    "focus": "geo_customer"
  }
  ```
- Prompt: system role = senior sales analyst; user role = context + yêu cầu 3–5 bullets tiếng Việt, có số liệu cụ thể.
- Error handling:
  - No key → markdown `⚠ Missing OPENAI_API_KEY in .env`
  - API error → markdown `⚠ LLM call failed: {error}`. Không crash.
  - Timeout 15s.

### 6.6 Explorer tab — PyGWalker

- Import: `from pygwalker.api.gradio import PYGWALKER_ROUTE, get_html_on_gradio` (cần verify trong implementation).
- Input: `df_filtered` lúc tab được mở. User kéo-thả dimension/measure → PyGWalker render chart.
- Fallback nếu PyGWalker không tương thích Gradio hiện tại: dropdown "chọn dimension X, measure Y, chart type Z" + Plotly render → note trong HANDOFF.

### 6.7 Theme & CSS — `theme.py`

- Base theme: `gr.themes.Soft()` + custom CSS string injected via `css=` parameter.
- Palette (match Canva background):
  - Header bg: `#3c3c40` (dark grey)
  - Page bg: `#f6f6f6`
  - Card bg: `#ffffff`
  - Accent: `#6b4eff` (purple/indigo, matching underline in backgrounds)
  - Text primary: `#1a1a1a`
- Cards: `border-radius: 16px; box-shadow: 0 2px 6px rgba(0,0,0,0.12)`.
- Font: Inter hoặc system-ui.

## 7. File structure

```
Regional Sales Summary/
├── app.py                              # Gradio Blocks UI, tab layout, callbacks
├── data.py                             # load_csv, apply_filters, summarize_for_llm
├── charts.py                           # 15+ chart builders
├── insights.py                         # rule templates, openai_client, prompt builder
├── theme.py                            # custom CSS string, color palette
├── .env                                # OPENAI_API_KEY (git-ignored)
├── .env.example                        # template committed
├── .gitignore                          # .env, .venv, __pycache__, .ipynb_checkpoints
├── pyproject.toml                      # + gradio, pygwalker, openai, python-dotenv
├── README.md                           # cách chạy, screenshot
├── CLAUDE.md                           # (đã có)
├── HANDOFF.md                          # progress + success criteria + resume prompt
├── docs/superpowers/specs/
│   └── 2026-04-18-regional-sales-gradio-design.md   # file này
├── plan.md                             # (sẽ sinh từ writing-plans skill sau)
├── Sales_data(EDA Exported).csv        # data source (giữ nguyên)
├── EDA_Regional_Sales_Analysis.ipynb
├── Regional Sales Dataset.xlsx
├── SALES REPORT.pbix
└── Dashboard Backround/                # PNG assets — giữ nguyên
```

## 8. Key decisions & trade-offs (recap Q&A)

| # | Decision | Chosen | Reason |
|---|---|---|---|
| Q1 | App goal | B+C hybrid: dashboard + explorer | PBI là reference, không phải clone |
| Q2 | Structure | 4 tabs (3 themed + Explorer) | Narrative + EDA exploration |
| Q3 | Filter scope | Global shared | Mượt, kể chuyện qua 3 góc nhìn |
| Q4 | Chart lib | Plotly + PyGWalker (Explorer) | Interactive + wow factor |
| Q5 | Insight | Rule-based + LLM button (B+C) | Dynamic + deep recommendation |
| Q6 | LLM | OpenAI `gpt-4o-mini`, on-demand, `.env` key | Rẻ, nhanh, an toàn khi demo |
| Q7 | Data source | Phase 1 hardcoded; Phase 2 hybrid upload (stretch) | Demo chắc chắn; mở rộng sau |
| Q8a | UI language | Hybrid: VN cho UI chrome + insight; EN cho chart/metric | Khớp convention analytics |
| Q8b | Theme | Custom CSS polish | Match Canva, điểm cộng môn Data Viz |
| Q9a | Deploy | Local only | An toàn khi demo |
| Q9b | Code | Hybrid: `app.py` + 3 helpers | Cân bằng đọc code vs organization |
| Q10a | Timeline | 3–4 ngày | |
| Q10b | Priority | y > z > w > x | interactivity > polish > narrative > quantity |
| Q10c | Analyses | Giữ đủ 15 | |

## 9. Roadmap — Alpha approach (tab by tab)

| Phase | Est. | Deliverable | Demo-able |
|---|---|---|---|
| **1. Foundation** | 3h | `data.py` + `theme.py` + `app.py` skeleton 4 tab + filter bar + CSS base | ✓ chạy được, filter có action |
| **2. Tab 1 Overview** | 4h | 5 KPI + 4 chart + rule insight | ✓ |
| **3. Tab 2 Product & Channel** | 3h | 5 chart (bar, pie, bar, box) + rule insight | ✓ |
| **4. Tab 3 Geo & Customer** | 5h | 6 chart + Top/Bottom toggle + rule insight | ✓ |
| **5. LLM integration** | 2h | OpenAI client, 3 button, error handling | ✓ (full demo) |
| **6. Tab 4 Explorer** | 2h | PyGWalker integrate hoặc fallback | ✓ |
| **7. Polish & docs** | 3h | CSS refine, empty-filter guard, README hoàn chỉnh, HANDOFF update | ✓ Sẵn sàng nộp |
| **8. Phase 2 stretch** | — | Upload CSV + schema validation (nếu dư) | — |

Tổng ~22h, trong 3–4 ngày.

## 10. Success criteria

1. App chạy `uv run python app.py` → Gradio mở browser localhost trong ≤ 3s.
2. Đổi bất kỳ filter nào → tất cả chart + rule insight update trong ≤ 1s.
3. 15 phân tích EDA hiển thị đầy đủ (manual smoke test).
4. Nút LLM trên Tab 1/2/3 trả về khuyến nghị tiếng Việt trong ≤ 10s.
5. Không có `OPENAI_API_KEY` → app vẫn chạy, LLM button báo lỗi rõ ràng (không crash).
6. Tab Explorer PyGWalker hoạt động: kéo-thả dimension/measure, vẽ chart dynamic. (Nếu fallback thì vẫn chọn chart được.)
7. Custom CSS áp dụng: header tối, card trắng bo tròn, font đồng bộ.
8. Filter rỗng (0 dòng kết quả) → hiển thị panel "Không có dữ liệu", không crash chart.

## 11. Open questions / Phase 2 deferred

- **Upload CSV**: Phase 2 stretch. Implement khi Phase 1 xác nhận ổn. Cần schema validator, column alias mapping.
- **Cross-filter** (click chart A → filter chart B): defer, yêu cầu custom JS trong Gradio. Khả năng thấp trước deadline.
- **HF Spaces deploy**: defer sau bảo vệ — link có thể bỏ vào portfolio/CV.
- **PyGWalker Gradio compatibility**: verify trong Phase 6. Nếu không tương thích, fallback = custom EDA mini (dropdown dimension + measure + chart type).
- **Multilingual LLM output**: hiện cố định tiếng Việt. Có thể thêm toggle sau.

## 12. Risks & mitigations

| Risk | Likelihood | Mitigation |
|---|---|---|
| PyGWalker không tích hợp Gradio mới | Med | Fallback dropdown-based mini-explorer; đã note trong spec |
| OpenAI API rate limit trong demo | Low | Cache kết quả LLM theo hash(filter_dict); backup screenshot insight |
| 64k rows Plotly chậm | Low | `lru_cache` filter; downsample scatter |
| Custom CSS vỡ layout trên màn hình nhỏ | Med | Test 1440p + 1080p; dùng responsive grid |
| Schema CSV đổi (Phase 2 upload) | High | Schema validator raise early với message rõ ràng |
| Mất `.env` → lộ API key | Low | `.gitignore` + `.env.example` commit |

---

**Next step**: User duyệt spec này → tôi invoke skill `writing-plans` để tạo `plan.md` chi tiết từng phase với checklist tasks cụ thể → bắt đầu implement Phase 1.
