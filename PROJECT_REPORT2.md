# Báo cáo Dự án: USA Regional Sales Analysis

**Phân tích Doanh số Bán hàng theo Vùng Miền — Từ đầu đến cuối (End-to-End)**
Từ Dữ liệu Thô (Excel) → Phân tích EDA (Python) → Bảng điều khiển Power BI → Ứng dụng Web Gradio tương tác

---

## Mục lục

1. [Tổng quan Dự án](#1-tổng-quan-dự-án)
2. [Xác định Vấn đề (Problem Statement)](#2-xác-định-vấn-đề-problem-statement)
3. [Đầu vào và Đầu ra](#3-đầu-vào-và-đầu-ra)
4. [Kiến trúc Đường ống Dữ liệu (Data Pipeline)](#4-kiến-trúc-đường-ống-dữ-liệu-data-pipeline)
5. [Cấu trúc thư mục dự án](#5-cấu-trúc-thư-mục-dự-án)
6. [Chi tiết từng File và nhiệm vụ](#6-chi-tiết-từng-file-và-nhiệm-vụ)
7. [Quy trình từ đầu đến cuối (End-to-End Workflow)](#7-quy-trình-từ-đầu-đến-cuối-end-to-end-workflow)
8. [Vấn đề với dữ liệu và cách xử lý](#8-vấn-đề-với-dữ-liệu-và-cách-xử-lý)
9. [15 Phân tích Khám phá Dữ liệu (EDA) và Kết quả](#9-15-phân-tích-khám-phá-dữ-liệu-eda-và-kết-quả)
10. [Ứng dụng Web Gradio — Bảng Điều khiển Tương tác](#10-ứng-dụng-web-gradio--bảng-điều-khiển-tương-tác)
11. [Hướng dẫn Cài đặt và Chạy dự án](#11-hướng-dẫn-cài-đặt-và-chạy-dự-án)
12. [Kết quả đạt được](#12-kết-quả-đạt-được)
13. [Kiến thức và Kỹ năng thể hiện](#13-kiến-thức-và-kỹ-năng-thể-hiện)

---

## 1. Tổng quan Dự án

**Tên dự án:** USA Regional Sales Analysis — Phân tích Doanh số Bán hàng theo Vùng Miền tại Mỹ
**Dữ liệu:** Giao dịch bán hàng của công ty thương mại Acme Co., giai đoạn 2014–2018
**Loại dự án:** Dự án danh mục (Portfolio Project), Phân tích dữ liệu từ đầu đến cuối (End-to-End Data Analytics)
**Môn học:** Trực quan hoá Dữ liệu

Đây là một dự án phân tích dữ liệu toàn diện bao trùm toàn bộ vòng đời của một chu trình phân tích dữ liệu thực tế:

- Thu thập và hiểu cấu trúc dữ liệu thô (Excel, 6 bảng quan hệ)
- Làm sạch, biến đổi, hợp nhất dữ liệu bằng Python (pandas)
- Phân tích khám phá dữ liệu (Exploratory Data Analysis — EDA) với 15 loại phân tích chuyên sâu
- Xây dựng bảng điều khiển (Dashboard) tương tác trên Power BI (3 trang, các phép đo DAX)
- Phát triển ứng dụng web Gradio (Python) thay thế Power BI — sản phẩm cuối cùng của khóa học

---

## 2. Xác định Vấn đề (Problem Statement)

Các đội bán hàng (sales) của Acme Co. **thiếu một góc nhìn tổng quan dựa trên dữ liệu** về hiệu suất của từng khu vực, sản phẩm, và kênh phân phối. Điều này gây ra:

- Khó khăn trong việc xác định **cơ hội tăng trưởng** theo vùng miền
- Phân bổ **ngân sách marketing** chưa hiệu quả theo mùa vụ
- Thiếu dữ liệu để **so sánh kế hoạch ngân sách (Budget) vs. thực tế (Actual)** cho năm 2017
- Không có cái nhìn rõ ràng về **phân khúc khách hàng** (ai đang mang lại giá trị cao nhất)

### Câu hỏi phân tích cần trả lời

1. Sản phẩm, kênh, và vùng địa lý nào mang lại **doanh thu và lợi nhuận cao nhất**?
2. Doanh thu có biến động theo **mùa vụ (seasonality)** không? Tháng nào là đỉnh điểm?
3. **Biên lợi nhuận (Profit Margin)** khác nhau như thế nào giữa các kênh phân phối?
4. Bang và vùng miền nào còn **dư địa tăng trưởng** chưa được khai thác?
5. Khách hàng nào cần được ưu tiên **giữ chân và bán thêm (upsell)**?

---

## 3. Đầu vào và Đầu ra

### Đầu vào (Input)

**File:** `Regional Sales Dataset.xlsx`
Chứa 6 trang tính (sheet) dữ liệu quan hệ với nhau:

| Tên trang tính | Số bản ghi | Vai trò |
|---|---|---|
| Sales Orders — Đơn hàng bán hàng | 64,104 | **Bảng Sự kiện (Fact Table)** — bảng giao dịch trung tâm |
| Customers — Khách hàng | 175 | Bảng Chiều (Dimension) — thông tin khách hàng |
| Products — Sản phẩm | 30 | Bảng Chiều — danh mục sản phẩm (30 mã hàng — SKU) |
| Regions — Khu vực địa lý | 994 | Bảng Chiều — thông tin địa lý (bang, vùng, toạ độ) |
| State Regions — Phân vùng tiểu bang | 49 | Bảng Chiều — phân nhóm tiểu bang theo khu vực nước Mỹ |
| 2017 Budgets — Ngân sách 2017 | 30 | Bảng Chiều — ngân sách kế hoạch năm 2017 theo sản phẩm |

### Đầu ra (Output)

| Sản phẩm | File | Mô tả |
|---|---|---|
| Dữ liệu đã làm sạch | `Sales_data(EDA Exported).csv` | 64,104 bản ghi × 21 cột, đã hợp nhất 6 bảng + xây dựng đặc trưng (Feature Engineering) |
| Phân tích khám phá dữ liệu (EDA) | `EDA_Regional_Sales_Analysis.ipynb` | Sổ ghi chép (Notebook) 80 ô lệnh (cells), 15 phân tích + biểu đồ + kết quả |
| Bảng điều khiển BI (BI Dashboard) | `SALES REPORT.pbix` | Bảng điều khiển Power BI 3 trang tương tác |
| Slide trình bày | `PPT --- Regional Sales Analysis.pptx` | Tóm tắt dự án cho các bên liên quan (stakeholders) |
| Ứng dụng Web | `app.py` + toàn bộ mã nguồn Python | Ứng dụng Gradio 4 tab, 16 biểu đồ Plotly, khuyến nghị từ AI |

---

## 4. Kiến trúc Đường ống Dữ liệu (Data Pipeline)

Toàn bộ dự án tuân theo kiến trúc Trích xuất–Biến đổi–Nạp (ETL — Extract, Transform, Load) tiêu chuẩn, tổ chức thành một chuỗi tuyến tính:

```
Regional Sales Dataset.xlsx          (Nguồn: 6 trang tính dữ liệu thô)
        |
        | pd.read_excel(sheet_name=None)
        v
EDA_Regional_Sales_Analysis.ipynb    (Xử lý: làm sạch, hợp nhất, EDA)
        |
        | df.to_csv(...)   [Cell 75]
        v
Sales_data(EDA Exported).csv         (File trung gian: 64,104 × 21 cột)
        |
        +-----------> SALES REPORT.pbix      (Bảng điều khiển Power BI)
        |
        +-----------> app.py (Gradio)        (Ứng dụng Web tương tác)
```

**Lưu ý quan trọng:** File CSV là **cầu nối trung tâm** — vừa là đầu ra của sổ ghi chép (notebook), vừa là đầu vào của cả Power BI lẫn ứng dụng Gradio. Nếu tái chạy notebook (thay đổi dữ liệu hoặc logic), phải làm mới (refresh) Power BI và khởi động lại ứng dụng Gradio.

---

## 5. Cấu trúc thư mục dự án

```
Regional Sales Summary/
│
├── Regional Sales Dataset.xlsx          # Dữ liệu gốc (ĐẦU VÀO)
├── Sales_data(EDA Exported).csv         # Dữ liệu đã xử lý (TRUNG GIAN / ĐẦU VÀO)
├── EDA_Regional_Sales_Analysis.ipynb    # Sổ ghi chép Python: làm sạch + EDA
├── SALES REPORT.pbix                    # Bảng điều khiển Power BI
├── PPT --- Regional Sales Analysis.pptx # Slide trình bày
│
├── app.py          # Ứng dụng Gradio — điểm khởi chạy (entry point)
├── data.py         # Logic tải và lọc dữ liệu
├── charts.py       # 16 hàm xây dựng biểu đồ (Plotly)
├── insights.py     # Nhận xét dựa trên quy tắc + Giao tiếp với mô hình ngôn ngữ lớn (LLM)
├── theme.py        # Màu sắc + CSS (thiết kế theo phong cách Grafana)
│
├── tests/
│   ├── conftest.py        # Bộ dữ liệu kiểm thử (Pytest fixtures)
│   ├── test_data.py       # 9 bài kiểm thử cho data.py
│   ├── test_charts.py     # 18 bài kiểm thử khói (smoke tests) cho charts.py
│   ├── test_insights.py   # 7 bài kiểm thử cho insights.py
│   └── test_kpis.py       # 4 bài kiểm thử cho compute_kpis()
│
├── pyproject.toml         # Khai báo các thư viện phụ thuộc (uv)
├── uv.lock                # Tệp khoá phiên bản (lock file — cài đặt lại giống hệt)
├── .env.example           # Mẫu biến môi trường (environment variables)
│
├── Summary.txt            # Tóm tắt nội dung bài giảng 325–328
├── USA_Regional_Sales_Analysis_Project_Documentation.txt  # Tài liệu dự án đầy đủ
├── CLAUDE.md              # Hướng dẫn cho trợ lý AI
├── HANDOFF.md             # Trạng thái triển khai ứng dụng Gradio
│
├── Dashboard Backround/   # Hình nền PNG cho Power BI (thiết kế trên Canva)
├── docs/superpowers/      # Đặc tả kỹ thuật + kế hoạch triển khai Gradio
└── anh/                   # Ảnh tham khảo thiết kế
```

---

## 6. Chi tiết từng File và nhiệm vụ

### 6.1 File dữ liệu nguồn

**`Regional Sales Dataset.xlsx`**
- Đầu vào duy nhất của toàn bộ dự án
- 6 trang tính tương ứng với 6 thực thể trong sơ đồ quan hệ (Sơ đồ Thực thể–Quan hệ — ERD: Entity-Relationship Diagram)
- Chứa dữ liệu giao dịch thực của Acme Co. từ 2014 đến đầu 2018

### 6.2 Sổ ghi chép Jupyter (Jupyter Notebook) — Trung tâm xử lý

**`EDA_Regional_Sales_Analysis.ipynb`** (80 ô lệnh — cells)
- Được viết cho Google Colab (Cell 10 có `drive.mount(...)` — thay bằng đường dẫn cục bộ khi chạy ngoại tuyến)
- Thực hiện toàn bộ quy trình: nhập → đánh giá hồ sơ dữ liệu → làm sạch → hợp nhất → xây dựng đặc trưng (Feature Engineering) → 15 phân tích EDA → xuất CSV

| Phạm vi ô lệnh (Cell) | Giai đoạn | Mô tả |
|---|---|---|
| 8–10 | Nhập thư viện và tải dữ liệu | Nhập thư viện, đọc 6 trang tính vào từ điển (dictionary) |
| 11–18 | Đánh giá hồ sơ dữ liệu (Data Profiling) | Kiểm tra giá trị null, kiểu dữ liệu, trùng lặp; sửa tiêu đề bảng State Regions |
| 19 | Đường ống hợp nhất (Merge Pipeline) | 5 lần hợp nhất (left join) liên tiếp |
| 20–25 | Làm sạch (Cleaning) | Loại cột thừa, đổi tên theo kiểu snake_case, gán null cho ngân sách không phải 2017 |
| 26 | Xây dựng đặc trưng (Feature Engineering) | Tạo cột profit, profit_margin_pct, order_month_name/num |
| 32 | Lọc năm 2018 | Loại dữ liệu 2018 (chỉ có tháng 1–2) |
| 33–74 | 15 Phân tích EDA | Biểu đồ + kết quả từng phân tích |
| 75 | Xuất CSV | Xuất file CSV cho Power BI và Gradio |

### 6.3 File CSV — Cầu nối trung tâm

**`Sales_data(EDA Exported).csv`** (64,104 bản ghi × 21 cột)

21 cột bao gồm:

| Tên cột | Nguồn gốc | Ý nghĩa |
|---|---|---|
| order_number — mã đơn hàng | Sales Orders | Khoá chính (Primary Key) định danh đơn hàng |
| order_date — ngày đặt hàng | Sales Orders | Ngày giao dịch (kiểu dữ liệu datetime) |
| customer_name — tên khách hàng | Customers | Tên khách hàng |
| channel — kênh phân phối | Sales Orders | Kênh: Wholesale / Distributor / Export |
| product_name — tên sản phẩm | Products | Tên sản phẩm (Product 1 → Product 30) |
| quantity — số lượng | Sales Orders | Số lượng sản phẩm trong đơn hàng |
| unit_price — đơn giá | Products | Giá bán một đơn vị sản phẩm |
| revenue — doanh thu | Sales Orders | Doanh thu = quantity × unit_price |
| cost — chi phí đơn vị | Products | Chi phí sản xuất/nhập một đơn vị |
| state — mã bang | Regions | Mã bang 2 ký tự (ví dụ: CA = California) |
| state_name — tên bang | Regions | Tên đầy đủ của bang |
| us_region — vùng miền | State Regions | Vùng: West / Northeast / South / Midwest |
| budget — ngân sách | 2017 Budgets | Ngân sách kế hoạch (chỉ có giá trị cho năm 2017) |
| order_month — kỳ tháng | (tính toán) | Tháng–năm dạng kỳ (M period) |
| **total_cost** — tổng chi phí | **Xây dựng đặc trưng** | quantity × cost |
| **profit** — lợi nhuận | **Xây dựng đặc trưng** | revenue − total_cost |
| **profit_margin_pct** — biên lợi nhuận % | **Xây dựng đặc trưng** | (profit / revenue) × 100 |
| **order_month_name** — tên tháng | **Xây dựng đặc trưng** | Tên tháng bằng tiếng Anh (January...) |
| **order_month_num** — số tháng | **Xây dựng đặc trưng** | Số tháng (1–12) để sắp xếp đúng thứ tự |
| latitude — vĩ độ | Regions | Toạ độ địa lý (dùng cho bản đồ) |
| longitude — kinh độ | Regions | Toạ độ địa lý (dùng cho bản đồ) |

### 6.4 Bảng điều khiển Power BI (Power BI Dashboard)

**`SALES REPORT.pbix`** — Bảng điều khiển tương tác 3 trang
Nguồn dữ liệu: `Sales_data(EDA Exported).csv` (không phải file Excel gốc)

Các phép đo DAX (DAX Measures) đã tạo trong bảng `Custom Measures`:
- `Profit Margin % = DIVIDE(SUM(profit), SUM(revenue), 0) * 100`
- `Revenue Per Order = DIVIDE(SUM(revenue), COUNT(order_number))`

**Tính năng đặc biệt:**
- Điều hướng trang (Page Navigation) bằng nút bấm
- Bảng lọc ẩn/hiện (Filter Panel) bằng thẻ đánh dấu (Bookmark)
- Chuyển đổi Top 5 / Bottom 5 khách hàng bằng thẻ đánh dấu
- Nút xoá toàn bộ bộ lọc (Clear All Slicers)
- Hình nền thiết kế trên Canva (các file PNG trong thư mục `Dashboard Backround/`)

### 6.5 Mã nguồn Ứng dụng Gradio

#### `data.py` — Tầng Dữ liệu (Data Layer)
- Không nhập (import) Gradio, hoàn toàn thuần Python/pandas
- `load_csv()`: đọc CSV, kiểm tra lược đồ (17 cột bắt buộc), chuyển đổi kiểu ngày tháng
- `apply_filters(df, filters_dict)`: lọc theo năm / kênh / vùng / sản phẩm; danh sách rỗng = không lọc chiều đó
- `compute_kpis(df)`: tính 5 chỉ số hiệu suất chính (KPI)
- `summarize_for_llm(df, filters, focus)`: tóm tắt dữ liệu thành JSON để gửi lên mô hình ngôn ngữ lớn (LLM)

#### `charts.py` — Tầng Biểu đồ (Chart Layer)
- Không nhập Gradio, hoàn toàn thuần Plotly
- 16 hàm xây dựng biểu đồ (builder functions), mỗi hàm nhận `df` và trả về biểu đồ `go.Figure`
- Tất cả đều có cơ chế bảo vệ khi dữ liệu rỗng (empty-df guard) — trả về biểu đồ trống với thông báo

#### `insights.py` — Tầng Nhận xét (Insight Layer)
- Không nhập Gradio
- 3 hàm nhận xét dựa trên quy tắc (rule-based): overview, product_channel, geo_customer — trả về Markdown
- `llm_recommendation()`: gọi OpenAI `gpt-4o-mini`, trả về 3–5 khuyến nghị chiến lược tiếng Việt

#### `theme.py` — Tầng Thiết kế (Design Layer)
- `COLORS` — từ điển màu sắc theo phong cách Grafana (tiêu đề tối, nền xám nhạt, điểm nhấn xanh dương)
- `PALETTE` — 6 màu thân thiện với người mù màu (colorblind-safe) dùng cho biểu đồ
- `CUSTOM_CSS` — CSS toàn cục cho toàn bộ giao diện

#### `app.py` — Tầng Giao diện (UI Layer)
- **File duy nhất nhập Gradio**
- `build_app()`: khởi tạo khối Gradio Blocks, thanh lọc toàn cục, 4 tab, quản lý trạng thái (state)
- Móc nối sự kiện (Event wiring): `.change()` → `build_filter_state` → `render_tab1/2/3` theo chuỗi

---

## 7. Quy trình từ đầu đến cuối (End-to-End Workflow)

### Giai đoạn 1 — Hiểu bài toán kinh doanh (Business Understanding)

Xác định bài toán: Acme Co. cần hiểu hiệu suất bán hàng theo vùng miền để tối ưu nguồn lực và tìm cơ hội tăng trưởng. Định nghĩa các câu hỏi phân tích cụ thể trước khi viết bất kỳ dòng mã nào.

### Giai đoạn 2 — Hiểu dữ liệu và Sơ đồ Quan hệ (ERD — Entity-Relationship Diagram)

Xây dựng sơ đồ ERD để hiểu cấu trúc quan hệ giữa 6 bảng:

```
Sales Orders (BẢNG SỰ KIỆN — FACT TABLE)
    ├── Customer Name Index  → Customers.Customer Index     (1 khách : N đơn hàng)
    ├── Product Description Index → Products.Index          (1 sản phẩm : N đơn hàng)
    ├── Delivery Region Index → Regions.id                  (1 vùng : N đơn hàng)
    ├── state_code → State Regions.State Code               (1 bang : N đơn hàng)
    └── [qua Products.Product Name] → 2017 Budgets          (liên kết gián tiếp)

Warehouse Code (Mã kho): không có bảng dimension tương ứng → bỏ qua
```

**Quyết định thiết kế quan trọng:** Luôn dùng phép nối trái (left join) — giữ toàn bộ 64,104 đơn hàng từ bảng sự kiện, không để mất bất kỳ giao dịch nào.

### Giai đoạn 3 — Thu thập Dữ liệu (Data Collection)

```python
# Đọc toàn bộ 6 trang tính cùng lúc vào một từ điển (dictionary)
sheets = pd.read_excel(file_path, sheet_name=None)
```

### Giai đoạn 4 — Làm sạch Dữ liệu (Data Cleaning — Cells 11–25)

Chi tiết trong [Phần 8](#8-vấn-đề-với-dữ-liệu-và-cách-xử-lý).

### Giai đoạn 5 — Xây dựng Đặc trưng (Feature Engineering — Cell 26)

Tạo các cột thông tin mới từ dữ liệu đã có:

```python
df['total_cost']          = df['quantity'] * df['cost']
df['profit']              = df['revenue'] - df['total_cost']
df['profit_margin_pct']   = (df['profit'] / df['revenue']) * 100
df['order_month_name']    = df['order_date'].dt.month_name()   # dùng cho biểu đồ
df['order_month_num']     = df['order_date'].dt.month          # dùng để sắp xếp trong Power BI
```

Cặp `order_month_name` + `order_month_num` bắt buộc phải có đồng thời: tên tháng để hiển thị trên trục X biểu đồ, số tháng để Power BI sắp xếp đúng thứ tự (nếu chỉ có tên, Power BI sắp xếp theo bảng chữ cái: April, August, December... thay vì January, February, March...).

### Giai đoạn 6 — Lọc năm 2018 (Cell 32)

```python
df_ = df[df['order_date'].dt.year != 2018]
```

Năm 2018 chỉ có dữ liệu tháng 1–2. Nếu giữ lại khi tính trung bình hoặc gộp theo tháng, các tháng 3–12 của 2018 sẽ bằng 0, làm lệch toàn bộ phân tích mùa vụ (seasonality). Dữ liệu 2018 vẫn được xuất vào CSV để Power BI có thể lọc riêng nếu cần.

### Giai đoạn 7 — 15 Phân tích Khám phá Dữ liệu (EDA — Cells 33–74)

Chi tiết trong [Phần 9](#9-15-phân-tích-khám-phá-dữ-liệu-eda-và-kết-quả).

### Giai đoạn 8 — Xuất file CSV (Cell 75)

```python
df.to_csv('Sales_data(EDA Exported).csv', index=False)
```

### Giai đoạn 9 — Xây dựng Bảng điều khiển Power BI (Power BI Dashboard)

1. Nhập CSV vào Power BI Desktop
2. Thiết kế hình nền 3 trang trên Canva (PNG)
3. Tạo bảng `Custom Measures`, viết các phép đo DAX
4. Dựng các hình ảnh trực quan (visuals) và cấu hình điều hướng/thẻ đánh dấu (navigation/bookmarks)

### Giai đoạn 10 — Ứng dụng Web Tương tác Gradio

Thay thế Power BI bằng ứng dụng web Python thuần, chạy được trên mọi hệ điều hành, không cần cài Power BI Desktop. Chi tiết trong [Phần 10](#10-ứng-dụng-web-gradio--bảng-điều-khiển-tương-tác).

---

## 8. Vấn đề với dữ liệu và cách xử lý

### Vấn đề 1 — Tiêu đề cột bị lệch ở bảng State Regions

**Triệu chứng:** Trang tính `State Regions` có dòng đầu tiên chứa dữ liệu thực, không phải tên cột. Khi pandas đọc vào, nó nhận dòng này làm tiêu đề → tên cột bị hiển thị là `0, 1, 2...` thay vì `State Code, Region...`

**Nguyên nhân:** File Excel bị định dạng sai — người tạo dữ liệu thêm dòng tiêu đề thủ công vào ô dữ liệu thay vì ô tiêu đề chuẩn của Excel.

**Cách xử lý:**
```python
# Lấy dòng đầu tiên (chứa tên cột bị sai vị trí) làm tiêu đề mới
new_header = df_state_regions.iloc[0]
df_state_regions.columns = new_header
# Xoá dòng đầu tiên đó đi và đặt lại số thứ tự (reset index)
df_state_regions = df_state_regions[1:].reset_index(drop=True)
```

### Vấn đề 2 — Ngân sách chỉ tồn tại cho năm 2017

**Triệu chứng:** Bảng `2017 Budgets` chứa ngân sách kế hoạch cho 30 sản phẩm nhưng chỉ cho năm 2017. Sau khi hợp nhất (merge) vào bảng Sales Orders, pandas tự động sao chép cột ngân sách này cho tất cả các năm (2014, 2015, 2016, 2017, 2018).

**Hậu quả nếu không xử lý:** Tổng ngân sách trên Power BI sẽ bị nhân lên 5 lần so với thực tế. Biểu đồ "Ngân sách so với Thực tế năm 2017" (Budget vs Actual 2017) sẽ hoàn toàn sai lệch.

**Cách xử lý:**
```python
# Gán giá trị rỗng (null) cho toàn bộ các dòng không thuộc năm 2017
df.loc[df['order_date'].dt.year != 2017, 'budget'] = pd.NA
```
Giá trị `pd.NA` (Null — rỗng) sẽ tự động bị bỏ qua bởi hàm `SUM()` trong cả pandas và Power BI.

### Vấn đề 3 — Dữ liệu năm 2018 không đầy đủ (Incomplete Data)

**Triệu chứng:** Năm 2018 chỉ có tháng 1 và tháng 2. Khi gộp tất cả năm để tính doanh thu trung bình theo tháng, 2018 kéo trung bình tháng 3–12 xuống thấp (10 tháng bằng 0), làm lệch hoàn toàn phân tích mùa vụ.

**Cách xử lý:** Loại năm 2018 khỏi các phân tích tổng hợp. Tuy nhiên vẫn giữ trong CSV để có thể xem riêng tháng 1–2/2018 nếu cần.

### Vấn đề 4 — Cột không có bảng chiều tương ứng

**Triệu chứng:** Cột `Warehouse Code` (Mã kho) trong Sales Orders không có trang tính nào khác để giải nghĩa.

**Cách xử lý:** Quyết định bỏ qua (drop) cột này — không thể phân tích theo kho hàng nếu không có thông tin mô tả kho.

### Vấn đề 5 — Cột thừa sau khi hợp nhất (Redundant Columns)

**Triệu chứng:** Sau 5 lần hợp nhất, xuất hiện nhiều cột trùng lặp (Customer Index, Index, id, State Code) và cột không liên quan (Múi giờ — Time zone, Dân số — Population, Diện tích mặt nước — Water Area, Mã vùng — Area Code, Tiền tệ — Currency...).

**Cách xử lý:**
```python
# Chỉ giữ lại các cột có giá trị phân tích
cols_to_keep = ['order_number', 'order_date', 'customer_name', 'channel', ...]
df = df[cols_to_keep]
```

**Nguyên tắc quan trọng:** Việc giữ hay bỏ cột nào phụ thuộc hoàn toàn vào **mục tiêu kinh doanh (Business Objective)**. Ví dụ: cột `Population` (Dân số) bị bỏ vì bài toán này chỉ cần phân tích doanh thu — nhưng nếu bài toán là "tỷ lệ thâm nhập thị trường" (Market Penetration = Doanh thu / Dân số), thì cột này lại rất quan trọng.

### Vấn đề 6 — Biểu đồ phân tán (Scatter) vô nghĩa với đơn giá rời rạc

**Triệu chứng:** Ban đầu dùng biểu đồ phân tán "Biên lợi nhuận vs Đơn giá". Nhưng `unit_price` chỉ có 30 giá trị cố định (30 SKU với giá cố định) → biểu đồ tạo ra 30 dải dọc thẳng đứng, không thể hiện bất kỳ xu hướng hay tương quan nào.

**Cách xử lý:** Thay bằng biểu đồ thanh nhóm (Grouped Bar Chart) "Doanh thu & Lợi nhuận theo Kênh" — cho thấy so sánh trực quan giữa doanh thu và lợi nhuận của từng kênh phân phối.

### Vấn đề 7 — Các lỗi giao diện trong ứng dụng Gradio (phát hiện khi chạy thật)

| Lỗi | Triệu chứng | Nguyên nhân gốc | Cách sửa |
|---|---|---|---|
| Chữ vô hình | Văn bản trong ô nhận xét / AI không đọc được (bôi chuột mới thấy) | Chủ đề tối (dark theme) của Gradio đặt `color: white` toàn cục, CSS của ứng dụng không ghi đè lại | Thêm `color: #0f172a !important` vào `.insight-panel *` và `.llm-output *` |
| Sắp xếp sản phẩm sai | "Product 1 → Product 10 → Product 11 → Product 2" (thứ tự chữ cái) | Python sắp xếp chuỗi theo bảng chữ cái mặc định | Đổi khoá sắp xếp thành `int(x.split()[-1])` cho chuỗi "Product N" |
| Cột biểu đồ histogram sát nhau | Các cột dính liền, khó đọc | Thiếu thuộc tính `bargap` trong bố cục biểu đồ | Thêm `bargap=0.08` vào `fig.update_layout()` |
| Biểu đồ phân tán vô nghĩa | Dải dọc, không có xu hướng | Đơn giá rời rạc (30 giá trị cố định) | Thay bằng biểu đồ thanh nhóm theo kênh |

---

## 9. Quá trình Phân tích Dữ liệu từ đầu đến cuối (Chi tiết theo từng bước)

Phần này trình bày **toàn bộ quy trình** thực hiện trong file `EDA_Regional_Sales_Analysis.ipynb` theo đúng thứ tự từng bước, bao gồm những gì đã làm, tại sao làm, và kết quả thu được.

---

### Bước 1 — Nhập thư viện và cấu hình môi trường (Cells 7–8)

**Thực hiện:** Nhập các thư viện Python cần thiết và cấu hình mặc định cho biểu đồ.

```python
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

%matplotlib inline               # Hiển thị biểu đồ trực tiếp trong notebook
sns.set_style("whitegrid")       # Nền trắng lưới — dễ đọc số liệu
plt.rcParams['figure.figsize'] = (10, 6)   # Kích thước mặc định cho mọi biểu đồ
```

**Vai trò từng thư viện:**
- `pandas` — đọc, làm sạch, và biến đổi dữ liệu dạng bảng
- `numpy` — tính toán số học
- `matplotlib` — vẽ biểu đồ nền tảng
- `seaborn` — vẽ biểu đồ thống kê đẹp hơn matplotlib

---

### Bước 2 — Tải dữ liệu từ file Excel (Cell 10)

**Thực hiện:** Đọc toàn bộ 6 trang tính (sheets) từ file Excel vào Python cùng một lúc.

```python
sheets = pd.read_excel(file_path, sheet_name=None)
# sheet_name=None → đọc TẤT CẢ sheets, trả về dict {tên_sheet: DataFrame}

df_sales    = sheets['Sales Orders']   # 64,104 dòng × 12 cột
df_customers = sheets['Customers']     # 175 dòng × 2 cột
df_products  = sheets['Products']      # 30 dòng × 2 cột
df_regions   = sheets['Regions']       # 994 dòng × 15 cột
df_state_reg = sheets['State Regions'] # 49 dòng × 3 cột (bị lỗi header)
df_budgets   = sheets['2017 Budgets']  # 30 dòng × 2 cột
```

**Kết quả — Kích thước dữ liệu gốc:**

| Tên DataFrame | Số dòng | Số cột | Nội dung |
|---|---|---|---|
| `df_sales` | 64,104 | 12 | Toàn bộ đơn hàng 2014–2018 |
| `df_customers` | 175 | 2 | Mã + Tên khách hàng |
| `df_products` | 30 | 2 | Mã + Tên sản phẩm |
| `df_regions` | 994 | 15 | Thông tin địa lý bang, toạ độ, dân số... |
| `df_state_reg` | 49 | 3 | Mã bang, Tên bang, Vùng miền |
| `df_budgets` | 30 | 2 | Tên sản phẩm + Ngân sách 2017 |

**Quan sát quan trọng từ `df_sales.head()`:**
- Ngày đặt hàng bắt đầu từ 01/01/2014
- Kênh phân phối (channel) gồm: Wholesale, Distributor, Export
- Ví dụ doanh thu dòng đầu: $14,994.6 / $25,868.7 / $5,869.2
- Cột `Warehouse Code` (Mã kho) = "AXW291" — xuất hiện nhưng không có bảng nào giải nghĩa

---

### Bước 3 — Đánh giá hồ sơ dữ liệu (Data Profiling — Cells 11–17)

**Mục tiêu:** Hiểu "sức khoẻ" của dữ liệu trước khi xử lý — có lỗi gì không? Thiếu gì không?

**3a — Kiểm tra giá trị rỗng (Null Check — Cell 16):**

```python
df_sales.isnull().sum()
```

**Kết quả:** Tất cả 12 cột của `df_sales` đều có **0 giá trị rỗng** — dữ liệu giao dịch hoàn toàn đầy đủ.

**3b — Kiểm tra dữ liệu trùng lặp (Duplicate Check — Cell 17):**

```python
len(df_sales) == len(df_sales.drop_duplicates())
# Kết quả: True
```

**Kết quả:** **Không có dòng trùng lặp** trong 64,104 đơn hàng.

**3c — Phát hiện lỗi header ở bảng State Regions (Cell 15):**

Khi xem `df_state_reg.head()`, phát hiện tên cột bị sai — dòng đầu tiên chứa tên cột thật (`State Code`, `State`, `Region`) thay vì ở hàng header. Xem chi tiết cách sửa ở [Phần 8 — Vấn đề 1](#vấn-đề-1--tiêu-đề-cột-bị-lệch-ở-bảng-state-regions).

---

### Bước 4 — Hợp nhất 6 bảng thành 1 (Merge Pipeline — Cell 19)

**Mục tiêu:** Tạo một DataFrame duy nhất chứa đầy đủ thông tin từ tất cả 6 bảng để phân tích.

**Chiến lược:** Luôn dùng `left join` (nối trái) để giữ toàn bộ 64,104 đơn hàng — không để mất bất kỳ giao dịch nào dù dimension có thiếu.

```python
# Bước 4.1 — Nối thông tin khách hàng
df = df_sales.merge(df_customers, how='left',
    left_on='Customer Name Index', right_on='Customer Index')
# → Thêm cột: Customer Names

# Bước 4.2 — Nối thông tin sản phẩm
df = df.merge(df_products, how='left',
    left_on='Product Description Index', right_on='Index')
# → Thêm cột: Product Name

# Bước 4.3 — Nối thông tin khu vực địa lý
df = df.merge(df_regions, how='left',
    left_on='Delivery Region Index', right_on='id')
# → Thêm 15 cột: county, state_code, state, lat, lon, population...

# Bước 4.4 — Nối thông tin vùng miền (từ state_code)
df = df.merge(df_state_reg[['State Code', 'Region']], how='left',
    left_on='state_code', right_on='State Code')
# → Thêm cột: Region (West/South/Midwest/Northeast)

# Bước 4.5 — Nối ngân sách 2017 (qua Product Name)
df = df.merge(df_budgets, how='left', on='Product Name')
# → Thêm cột: 2017 Budgets

# Xoá cột khoá trùng lặp sau merge
df.drop(columns=['Customer Index', 'Index', 'id', 'State Code'], inplace=True)
```

**Kết quả sau merge:** 64,104 dòng × **30 cột** (tăng từ 12 cột ban đầu).

---

### Bước 5 — Làm sạch và thu gọn cột (Cells 20–22)

**5a — Chuẩn hoá tên cột (Cell 20):**

```python
df.columns = df.columns.str.lower()   # Chuyển tất cả về chữ thường
```

**5b — Chọn 15 cột có giá trị, đổi tên rõ ràng (Cell 21):**

Từ 30 cột sau merge, chỉ giữ lại 15 cột thực sự cần thiết cho phân tích doanh số. Bỏ các cột không liên quan: múi giờ (time_zone), dân số (population), diện tích mặt nước (water_area), mã vùng (area_code), thu nhập trung vị (median_income), tiền tệ (currency_code), mã kho (warehouse_code)...

| Tên gốc | Đổi thành | Ý nghĩa |
|---|---|---|
| ordernumber | order_number | Mã đơn hàng (duy nhất) |
| orderdate | order_date | Ngày đặt hàng |
| customer names | customer_name | Tên khách hàng |
| channel | channel | Kênh phân phối |
| product name | product_name | Tên sản phẩm |
| order quantity | quantity | Số lượng đặt |
| unit price | unit_price | Đơn giá ($) |
| line total | **revenue** | Doanh thu (đổi tên rõ hơn) |
| total unit cost | cost | Chi phí đơn vị |
| state_code | state | Mã bang 2 ký tự |
| state | state_name | Tên bang đầy đủ |
| region | us_region | Vùng miền (West/South/...) |
| latitude | lat | Vĩ độ địa lý |
| longitude | lon | Kinh độ địa lý |
| 2017 budgets | budget | Ngân sách kế hoạch |

**5c — Xử lý cột ngân sách (Budget Logic — Cell 22):**

```python
# Gán null cho tất cả dòng không phải năm 2017
df.loc[df['order_date'].dt.year != 2017, 'budget'] = pd.NA
```

**Kết quả:** Cột `budget` có **15,263 giá trị hợp lệ** (đơn hàng 2017) và **48,841 giá trị null** (2014–2016, 2018). Xem lý do chi tiết ở [Phần 8 — Vấn đề 2](#vấn-đề-2--ngân-sách-chỉ-tồn-tại-cho-năm-2017).

**5d — Xác nhận cấu trúc cuối (Cell 23 — `df.info()`):**

| # | Cột | Kiểu dữ liệu | Không-null |
|---|---|---|---|
| 0 | order_number | object (chuỗi) | 64,104 |
| 1 | order_date | datetime64[ns] | 64,104 |
| 2 | customer_name | object | 64,104 |
| 3 | channel | object | 64,104 |
| 4 | product_name | object | 64,104 |
| 5 | quantity | int64 (số nguyên) | 64,104 |
| 6 | unit_price | float64 (số thực) | 64,104 |
| 7 | revenue | float64 | 64,104 |
| 8 | cost | float64 | 64,104 |
| 9 | state | object | 64,104 |
| 10 | state_name | object | 64,104 |
| 11 | us_region | object | 64,104 |
| 12 | lat | float64 | 64,104 |
| 13 | lon | float64 | 64,104 |
| 14 | budget | float64 | **15,263** (chỉ 2017) |

---

### Bước 6 — Xây dựng Đặc trưng mới (Feature Engineering — Cell 26)

**Mục tiêu:** Tạo các cột mới chứa thông tin phân tích quan trọng mà dữ liệu gốc chưa có sẵn.

```python
# Tổng chi phí mỗi dòng đơn hàng
df['total_cost'] = df['quantity'] * df['cost']

# Lợi nhuận tuyệt đối mỗi dòng
df['profit'] = df['revenue'] - df['total_cost']

# Biên lợi nhuận theo %
df['profit_margin_pct'] = (df['profit'] / df['revenue']) * 100

# Tên tháng (dùng cho trục X biểu đồ)
df['order_month_name'] = df['order_date'].dt.month_name()

# Số tháng (dùng để sắp xếp đúng thứ tự trong Power BI)
df['order_month_num'] = df['order_date'].dt.month
```

**Ví dụ dòng đầu tiên sau Feature Engineering:**

| Cột | Giá trị |
|---|---|
| quantity | 10 |
| unit_price | $1,499.46 |
| revenue | $14,994.6 |
| cost | $1,094.6 |
| total_cost | $10,946.06 |
| **profit** | **$4,048.54** |
| **profit_margin_pct** | **27.0%** |
| order_month_name | "January" |
| order_month_num | 1 |

**Kết quả:** DataFrame cuối cùng có **64,104 dòng × 20 cột** (thêm 5 cột mới).

---

### Bước 7 — Phân tích 1: Xu hướng Doanh thu Hàng tháng (Cells 28–30)

**Loại phân tích:** Phân tích thời gian (Temporal Analysis)
**Biểu đồ:** Đường (Line Chart) với điểm đánh dấu (markers)

**Thực hiện:**
```python
# Tạo cột kỳ tháng (2014-01, 2014-02, ...)
df['order_month'] = df['order_date'].dt.to_period('M')
# Tính tổng doanh thu mỗi tháng
monthly_revenue = df.groupby('order_month')['revenue'].sum()
```

**Trục X:** Tháng từ 2014-01 đến 2018-02 (xoay 45 độ)
**Trục Y:** Tổng doanh thu (hiển thị dạng "24.0M", "26.0M"...)

**Kết quả và Nhận xét:**
- Doanh thu dao động ổn định trong khoảng **$23M – $26.5M/tháng** suốt 4 năm
- Xuất hiện **đỉnh rõ ràng vào tháng 5–6** mỗi năm
- **Đáy thấp nhất vào tháng 1** mỗi năm — bắt đầu năm doanh thu thường yếu
- Điểm bất thường đáng chú ý: **đầu 2017 tụt xuống ~$21.2M** — thấp hơn mức bình thường, cần điều tra nguyên nhân
- Xu hướng tổng thể **ổn định theo năm** — không có tăng trưởng tích luỹ rõ ràng (flat trend)

---

### Bước 8 — Phân tích 2: Xu hướng Theo tháng Gộp Tất cả Năm (Cells 31–33)

**Loại phân tích:** Phân tích mùa vụ (Seasonality Analysis)
**Biểu đồ:** Đường (Line Chart)

**Lý do loại năm 2018:**
```python
df_ = df[df['order_date'].dt.year != 2018]
# 2018 chỉ có Jan–Feb → nếu giữ lại, tháng 3–12 của 2018 = $0
# → làm sai lệch trung bình theo tháng khi gộp tất cả năm
```

**Thực hiện:** Gộp tất cả 2014–2017, tính **tổng** doanh thu từng tháng qua các năm.

**Kết quả số liệu thực tế:**

| Tháng | Tổng doanh thu (gộp 4 năm) |
|---|---|
| January | ~$99M |
| February | ~$98M |
| March | ~$97M |
| **April** | **~$95M (thấp nhất)** |
| **May** | **~$102M (cao nhất)** |
| June | ~$101M |
| July | ~$100M |
| **August** | **~$102M (cao thứ 2)** |
| September | ~$101M |
| October | ~$100M |
| November | ~$99M |
| December | ~$99M |

**Nhận xét:**
- Tháng **5 và 8** là 2 đỉnh cao nhất (~$102M mỗi tháng)
- Tháng **4** là đáy thấp nhất (~$95M) — doanh thu giảm sau quý 1
- Từ tháng 9–12 doanh thu ổn định ~$99–101M — không có đỉnh cuối năm (Acme Co. không phụ thuộc vào mùa lễ hội)
- **Chiến lược:** Tăng tồn kho và ngân sách marketing trước tháng 5 và tháng 8

---

### Bước 9 — Phân tích 3: Top 10 Sản phẩm theo Doanh thu (Cells 34–36)

**Loại phân tích:** Phân tích đơn biến (Univariate Analysis)
**Biểu đồ:** Thanh nằm ngang (Horizontal Bar Chart)

```python
top_products = df.groupby('product_name')['revenue'].sum() / 1e6
top_products = top_products.nlargest(10)
```

**Kết quả — Top 10 sản phẩm theo doanh thu:**

| Hạng | Sản phẩm | Doanh thu |
|---|---|---|
| 1 | **Product 26** | **~$118M** |
| 2 | **Product 25** | **~$110M** |
| 3 | Product 13 | ~$78M |
| 4–6 | Product 6, 10, 19 | ~$68–$75M |
| 7–10 | Product 3, 22, 7, 14 | ~$52–$57M |

**Nhận xét:** Product 26 và 25 dẫn đầu vượt trội — cách xa nhóm thứ 3 tới $30M. Đây là 2 sản phẩm cần được đảm bảo tồn kho tuyệt đối và ưu tiên trong kế hoạch sản xuất.

---

### Bước 10 — Phân tích 4: Top 10 Sản phẩm theo Lợi nhuận Trung bình (Cells 37–39)

**Loại phân tích:** Phân tích đơn biến
**Biểu đồ:** Thanh nằm ngang

```python
top_margin = df.groupby('product_name')['profit'].mean().nlargest(10)
```

**Kết quả — Top 10 sản phẩm lợi nhuận trung bình mỗi giao dịch:**

| Hạng | Sản phẩm | Lợi nhuận TB/giao dịch |
|---|---|---|
| 1 | **Product 28** | **~$8,300** |
| 2 | **Product 18** | **~$8,000** |
| 3 | Product 5 | ~$7,900 |
| 4 | Product 11 | ~$7,850 |
| 5–7 | Product 12, 26, 21 | ~$7,700–$7,800 |
| 8–10 | Product 4, 16, 1 | ~$7,400–$7,600 |

**Nhận xét quan trọng:** Product 26 vừa có doanh thu cao nhất (#1) vừa nằm top lợi nhuận trung bình (#6) → đây là sản phẩm "vàng" — bán nhiều lại còn lời tốt. Product 28 lợi nhuận TB cao nhất nhưng không xuất hiện trong top doanh thu → ít đơn hàng nhưng mỗi đơn rất lời.

---

### Bước 11 — Phân tích 5: Doanh thu theo Kênh Phân phối (Cells 40–42)

**Loại phân tích:** Phân tích đơn biến
**Biểu đồ:** Biểu đồ tròn (Pie Chart)

```python
channel_revenue = df.groupby('channel')['revenue'].sum().sort_values(ascending=False)
```

**Kết quả:**

| Kênh | % Doanh thu | Đặc điểm |
|---|---|---|
| **Wholesale** (Bán sỉ) | **54%** | Kênh chủ lực, đơn hàng lớn |
| **Distributor** (Nhà phân phối) | **31%** | Kênh trung gian |
| **Export** (Xuất khẩu) | **15%** | Ít nhất nhưng margin cao nhất |

**Nhận xét:** Acme Co. đang phụ thuộc nặng vào kênh bán sỉ nội địa. Kênh Export chỉ 15% — đây là cơ hội chưa được khai thác triệt để.

---

### Bước 12 — Phân tích 6: Phân phối Giá trị Đơn hàng (Cells 43–45)

**Loại phân tích:** Phân tích đơn biến
**Biểu đồ:** Biểu đồ tần suất (Histogram) — 50 khoảng

```python
order_values = df.groupby('order_number')['revenue'].sum()
# → Tổng giá trị từng đơn hàng (1 đơn có thể có nhiều dòng sản phẩm)
```

**Kết quả:**
- Phần lớn đơn hàng có giá trị từ **$20K đến $120K**
- Giá trị phổ biến nhất (mode): **$50K – $60K/đơn**
- Phân phối **lệch phải mạnh (right-skewed)** — một số ít đơn hàng cực lớn ($400K–$500K) kéo đuôi dài
- Sự tồn tại của đuôi phải → không nên dùng giá trị trung bình (mean) để mô tả đơn hàng điển hình — hãy dùng **trung vị (median)**

**Nhận xét:** Các đơn hàng cực lớn (bulk orders) có thể là đơn đặc biệt từ khách hàng lớn — cần xem xét riêng tránh làm sai lệch thống kê bình thường.

---

### Bước 13 — Phân tích 7: Biên Lợi nhuận vs. Đơn giá (Cells 46–48)

**Loại phân tích:** Phân tích song biến (Bivariate)
**Biểu đồ:** Biểu đồ phân tán (Scatter Plot)

```python
plt.scatter(df['unit_price'], df['profit_margin_pct'], alpha=0.6, color='green')
```

**Trục X:** Đơn giá (từ gần $0 đến >$6,500)
**Trục Y:** Biên lợi nhuận % (từ âm đến ~60%)

**Kết quả:**
- Biên lợi nhuận tập trung trong dải **18% – 60%**
- **Không có tương quan rõ ràng** giữa đơn giá và biên lợi nhuận
- Biểu đồ tạo **30 dải dọc thẳng đứng** — do unit_price chỉ có 30 giá trị cố định (30 SKU)
- Một số điểm ngoại lệ dưới 18% ở cả mức giá thấp lẫn cao

**Nhận xét:** Phân tích này xác nhận rằng **giá bán không quyết định lợi nhuận** — cùng một sản phẩm có thể có margin rất khác nhau tuỳ giao dịch. Trong ứng dụng Gradio, biểu đồ này được thay bằng "Doanh thu & Lợi nhuận theo Kênh" vì trực quan hơn và có ý nghĩa kinh doanh rõ hơn.

---

### Bước 14 — Phân tích 8: Phân phối Đơn giá từng Sản phẩm (Cells 49–51)

**Loại phân tích:** Phân tích song biến
**Biểu đồ:** Biểu đồ hộp (Box Plot)

```python
sns.boxplot(data=df, x='product_name', y='unit_price')
```

**Trục X:** 30 tên sản phẩm (xoay 45 độ)
**Trục Y:** Đơn giá ($)

**Kết quả — Các ngoại lệ đáng chú ý:**

| Sản phẩm | Vấn đề |
|---|---|
| Product 8, 17, 27, 20, 28 | Có đơn giá **cực cao** vượt xa hộp — bulk/premium orders bất thường |
| Product 20, 27 | Có đơn giá **gần $0** — có thể là hàng khuyến mãi, hàng test, hoặc lỗi dữ liệu |

**Nhận xét:** Sự tồn tại của ngoại lệ giá cả chứng tỏ không phải mọi giao dịch đều ở "giá tiêu chuẩn" — cần loại bỏ các ngoại lệ này khi tính giá trung bình cho báo cáo định giá.

---

### Bước 15 — Phân tích 9: Doanh thu theo Vùng miền (Cells 52–54)

**Loại phân tích:** Phân tích đơn biến (Geospatial)
**Biểu đồ:** Thanh nằm ngang (Horizontal Bar Chart)

```python
region_revenue = df.groupby('us_region')['revenue'].sum() / 1e6
```

**Kết quả:**

| Vùng miền | Doanh thu | % Tổng |
|---|---|---|
| **West** (Tây) | **~$360M** | **~35%** |
| **South** (Nam) | ~$320M | ~32% |
| **Midwest** (Trung Tây) | ~$320M | ~32% |
| **Northeast** (Đông Bắc) | ~$210M | **~20%** |

**Nhận xét:** South và Midwest có mức tương đương nhau. Northeast thấp hơn hẳn — chỉ bằng 58% của West — nhưng đây là vùng có mật độ kinh tế cao (New York, Massachusetts, Connecticut...) → **cơ hội tăng trưởng lớn chưa được khai thác**.

---

### Bước 16 — Phân tích 10: Bản đồ Doanh thu theo Bang (Cells 56–58)

**Loại phân tích:** Phân tích không gian địa lý (Geospatial Analysis)
**Biểu đồ:** Bản đồ tô màu (Choropleth Map — Plotly Interactive)

```python
state_revenue = df.groupby('state')['revenue'].sum() / 1e6
fig = px.choropleth(state_revenue, locations='state',
    locationmode='USA-states', color='revenue',
    scope='usa', color_continuous_scale='Blues')
```

**Đặc điểm:** Biểu đồ **tương tác** (Plotly) — di chuột vào bang sẽ hiện số liệu chính xác.

**Kết quả — Top 10 bang theo doanh thu:**

| Hạng | Bang | Doanh thu |
|---|---|---|
| 1 | **California (CA)** | **~$230M** |
| 2 | Illinois (IL) | ~$112M |
| 3 | Florida (FL) | ~$90M |
| 4 | Texas (TX) | ~$85M |
| 5 | New York (NY) | ~$55M |
| 6 | Indiana (IN) | ~$54M |
| 7 | New Jersey (NJ) | ~$47M |
| 8 | Massachusetts (MA) | ~$44M |
| 9 | Michigan (MI) | ~$40M |
| 10 | Connecticut (CT) | ~$35M |

**Nhận xét:** California **gấp đôi bang thứ 2** (IL). Sự tập trung quá cao vào 1 bang là rủi ro — nếu thị trường California suy yếu, toàn bộ doanh thu bị ảnh hưởng nặng.

---

### Bước 17 — Phân tích 11: Top 10 Bang — Doanh thu & Số đơn hàng (Cell 66)

**Loại phân tích:** Phân tích song biến
**Biểu đồ:** 2 biểu đồ thanh riêng biệt (Revenue và Orders)

```python
state_agg = df.groupby('state_name').agg(
    revenue=('revenue', 'sum'),
    orders=('order_number', 'nunique')
).nlargest(10, 'revenue')
```

**Kết quả — So sánh Doanh thu và Số đơn:**

| Bang | Doanh thu | Số đơn hàng |
|---|---|---|
| **California** | **~$230M** | **~7,500+** |
| Illinois | ~$112M | ~4,600 |
| Florida | ~$90M | ~3,700 |
| Texas | ~$85M | ~3,600 |
| New York | ~$55M | ~2,500 |
| Indiana | ~$54M | ~2,500 |

**Nhận xét:** California dẫn đầu **trên cả 2 chiều** — không chỉ mỗi đơn hàng giá trị cao mà còn có nhiều đơn nhất. Illinois đứng thứ 2 cả doanh thu lẫn số đơn. Không có bang nào "lạc nhịp" (doanh thu cao nhưng rất ít đơn hoặc ngược lại).

---

### Bước 18 — Phân tích 12: Biên Lợi nhuận theo Kênh (Cells 62–64)

**Loại phân tích:** Phân tích song biến
**Biểu đồ:** Thanh đứng có nhãn số (Annotated Bar Chart)

```python
channel_margin = df.groupby('channel')['profit_margin_pct'].mean().sort_values(ascending=False)
```

**Kết quả — Biên lợi nhuận trung bình theo kênh:**

| Kênh | Biên lợi nhuận TB | So sánh |
|---|---|---|
| **Export** (Xuất khẩu) | **37.93%** | Cao nhất |
| **Distributor** (Nhà phân phối) | **37.56%** | Giữa |
| **Wholesale** (Bán sỉ) | **37.09%** | Thấp nhất |

**Nhận xét quan trọng:** Chênh lệch giữa 3 kênh rất nhỏ (dưới 0.9%) — có nghĩa là cả 3 kênh đều **duy trì biên lợi nhuận tương đương nhau**. Tuy nhiên Export vừa có margin cao nhất lại vừa chỉ chiếm 15% doanh thu → **đây là kênh có tiềm năng mở rộng nhất** mà không lo làm giảm lợi nhuận.

---

### Bước 19 — Phân tích 13: Top và Bottom 10 Khách hàng (Cells 60–61)

**Loại phân tích:** Phân tích so sánh (Comparative Analysis)
**Biểu đồ:** 2 biểu đồ thanh ngang cạnh nhau (Side-by-Side Horizontal Bars)

```python
cust_revenue = df.groupby('customer_name')['revenue'].sum() / 1e6
top10 = cust_revenue.nlargest(10)
bottom10 = cust_revenue.nsmallest(10)
```

**Kết quả — Top 10 khách hàng doanh thu cao nhất:**

| Hạng | Khách hàng | Doanh thu |
|---|---|---|
| 1 | **Aibox Company** | **~$12.5M** |
| 2 | State Ltd | ~$12.2M |
| 3 | Brite-Tech Inc | ~$11.8M |
| ... | ... | ~$10–11M |
| 10 | Deseret Group | ~$9.9M |

**Kết quả — Bottom 10 khách hàng doanh thu thấp nhất:**

| Hạng | Khách hàng | Doanh thu |
|---|---|---|
| 165 | BB17 Company | ~$4.1M |
| 166 | Johnson Ltd | ~$4.2M |
| ... | ... | ~$4–5M |
| 174 | (khách hàng ít nhất) | ~$5.1M |

**Nhận xét:** Ngay cả bottom 10 khách hàng cũng có doanh thu $4–5M — cho thấy Acme Co. không có khách hàng "siêu nhỏ". Khoảng cách từ $12.5M (top) xuống $4.1M (bottom) là **3 lần** — không quá tập trung ở top như nhiều công ty khác.

---

### Bước 20 — Phân tích 14: Phân khúc Khách hàng — Bubble Chart (Cells 67–69)

**Loại phân tích:** Phân tích đa biến (Multivariate Analysis)
**Biểu đồ:** Bong bóng (Bubble Chart — 3 chiều trong 1 biểu đồ)

```python
cust_seg = df.groupby('customer_name').agg(
    total_revenue=('revenue', 'sum'),
    avg_margin=('profit_margin_pct', 'mean'),
    orders=('order_number', 'nunique')
)
```

**3 chiều được thể hiện:**
- **Trục X:** Tổng doanh thu ($M)
- **Trục Y:** Biên lợi nhuận trung bình (%)
- **Kích thước bong bóng:** Số đơn hàng

**Kết quả — Các nhóm khách hàng phát hiện:**

| Nhóm | Đặc điểm | Ý nghĩa |
|---|---|---|
| **Khách hàng vàng** | Doanh thu >$10M, margin 36–40%, bong bóng lớn | Ưu tiên tối đa — giữ chân bằng mọi giá |
| **Khách hàng tiềm năng** | Margin cao (~38–43%) nhưng doanh thu $6–8M | Có thể upsell — họ "lời" nhiều nhưng chưa mua đủ |
| **Khách hàng trung bình** | Doanh thu $6–10M, margin ~34–38% | Ổn định, duy trì quan hệ |
| **Khách hàng cần xem lại** | Doanh thu thấp <$6M, margin thấp <34% | Cân nhắc chiến lược re-engagement hoặc điều chỉnh giá |

**Phát hiện quan trọng:** Khách hàng có doanh thu >$10M vẫn duy trì **margin 36–40%** — chứng tỏ **quy mô không làm giảm lợi nhuận**. Acme Co. không phải chiết khấu quá nhiều để giữ khách hàng lớn.

---

### Bước 21 — Phân tích 15: Ma trận Tương quan (Cells 70–72)

**Loại phân tích:** Phân tích đa biến
**Biểu đồ:** Bản đồ nhiệt (Heatmap) có chú thích số

```python
num_cols = ['quantity', 'unit_price', 'revenue', 'cost', 'profit']
corr_matrix = df[num_cols].corr()
sns.heatmap(corr_matrix, annot=True, fmt='.2f', cmap='viridis')
```

**Kết quả — Ma trận tương quan đầy đủ:**

| | quantity | unit_price | revenue | cost | profit |
|---|---|---|---|---|---|
| **quantity** | 1.00 | ~0.00 | 0.34 | ~0.00 | 0.30 |
| **unit_price** | ~0.00 | 1.00 | **0.91** | **0.94** | 0.79 |
| **revenue** | 0.34 | **0.91** | 1.00 | 0.85 | **0.87** |
| **cost** | ~0.00 | **0.94** | 0.85 | 1.00 | 0.58 |
| **profit** | 0.30 | 0.79 | **0.87** | 0.58 | 1.00 |

**Diễn giải từng cặp quan trọng:**

| Cặp biến | Tương quan | Ý nghĩa |
|---|---|---|
| unit_price ↔ cost | **0.94** (rất mạnh) | Sản phẩm đắt = chi phí sản xuất cao — hợp lý |
| unit_price ↔ revenue | **0.91** (rất mạnh) | Đơn giá cao → doanh thu cao hơn |
| profit ↔ revenue | **0.87** (mạnh) | **Tăng doanh thu → lợi nhuận tăng theo** |
| cost ↔ revenue | 0.85 (mạnh) | Chi phí cao → doanh thu cũng cao |
| unit_price ↔ profit | 0.79 (khá mạnh) | Sản phẩm giá cao có xu hướng lợi nhuận tốt hơn |
| quantity ↔ revenue | 0.34 (yếu) | Bán nhiều hơn không tự động tăng doanh thu nhiều |
| quantity ↔ unit_price | **~0.00** (không tương quan) | Số lượng đặt không liên quan gì đến giá cả |

**Kết luận phân tích:** **Đơn giá (unit_price) là nhân tố quan trọng nhất** — ảnh hưởng mạnh đến cả doanh thu và lợi nhuận. Số lượng đặt hàng (quantity) hầu như không ảnh hưởng đến giá cả — khách hàng không được chiết khấu theo số lượng một cách có hệ thống.

---

### Bước 22 — Xuất file CSV (Cell 75)

**Thực hiện:**
```python
df.to_csv('Sales_data(EDA Exported).csv', index=False)
```

**File xuất ra có:**
- **64,104 dòng** (toàn bộ đơn hàng 2014–2018, bao gồm cả 2018)
- **21 cột** (15 cột gốc + 6 cột mới từ Feature Engineering: total_cost, profit, profit_margin_pct, order_month_name, order_month_num, order_month)
- **Không có cột index** (`index=False`) — tiết kiệm dung lượng, tránh cột số thứ tự dư thừa

**Mục đích:** File này là cầu nối để đưa dữ liệu đã làm sạch sang Power BI và ứng dụng Gradio.

---

### Tổng hợp: Bảng tra cứu nhanh 15 Phân tích EDA

| # | Tên phân tích | Loại | Biểu đồ | Kết quả số thực tế | Nhận xét chính |
|---|---|---|---|---|---|
| 1 | Xu hướng doanh thu hàng tháng | Thời gian | Đường | $23M–$26.5M/tháng | Ổn định; đỉnh May–June; đáy January |
| 2 | Xu hướng theo tháng (gộp năm) | Mùa vụ | Đường | May & Aug ~$102M; Apr ~$95M | Tháng 5 cao nhất; tháng 4 thấp nhất |
| 3 | Top 10 sản phẩm theo doanh thu | Đơn biến | Thanh ngang | P26=$118M; P25=$110M; P13=$78M | P26 dẫn đầu cách xa |
| 4 | Top 10 sản phẩm theo lợi nhuận TB | Đơn biến | Thanh ngang | P28=$8,300; P18=$8,000/giao dịch | P26 vừa top doanh thu vừa top lợi nhuận |
| 5 | Doanh thu theo kênh | Đơn biến | Tròn | Wholesale 54%; Dist 31%; Export 15% | Export thấp nhất nhưng margin cao nhất |
| 6 | Phân phối giá trị đơn hàng | Đơn biến | Histogram | Mode $50–60K; đuôi đến $500K | Right-skewed; dùng median thay mean |
| 7 | Margin vs Đơn giá | Song biến | Scatter | Không tương quan rõ | 30 dải dọc — giá rời rạc |
| 8 | Đơn giá từng sản phẩm | Song biến | Box plot | P8,17,27 có outlier cực cao | Cần loại outlier khi tính trung bình |
| 9 | Doanh thu theo vùng miền | Đơn biến | Thanh ngang | West $360M; NE $210M | Northeast thấp nhất — dư địa lớn |
| 10 | Doanh thu theo bang (Map) | Địa lý | Choropleth | CA=$230M; IL=$112M; FL=$90M | CA gấp đôi bang thứ 2 |
| 11 | Top bang: DT + Đơn hàng | Song biến | Thanh kép | CA: $230M & 7,500+ đơn | CA dẫn đầu cả 2 chiều |
| 12 | Margin theo kênh | Song biến | Thanh có nhãn | Export 37.93%; Dist 37.56%; WS 37.09% | Chênh <0.9%; Export cần mở rộng |
| 13 | Top/Bottom 10 khách hàng | So sánh | Thanh ngang đôi | Aibox $12.5M; Bottom ~$4.1M | Khoảng cách 3x — khá đều |
| 14 | Phân khúc khách hàng | Đa biến | Bubble chart | KH >$10M: margin 36–40% | Quy mô không giảm lợi nhuận |
| 15 | Ma trận tương quan | Đa biến | Heatmap | P↔R=0.87; UP↔C=0.94; Q↔UP≈0 | Đơn giá là nhân tố quan trọng nhất |

---

### Khuyến nghị Chiến lược rút ra từ toàn bộ EDA

1. **Mở rộng kênh Export** — margin cao nhất (37.93%) nhưng chỉ 15% doanh thu; đầu tư marketing và mạng lưới phân phối quốc tế
2. **Tập trung vùng Northeast** — thấp nhất (20%) trong khi mật độ kinh tế cao; cần thêm nhà phân phối khu vực
3. **Tăng tồn kho và marketing trước tháng 5** — đỉnh mùa vụ, cần chuẩn bị trước 1–2 tháng
4. **Ưu tiên giữ chân Top 10 khách hàng** — chiếm tỷ trọng lớn, margin tốt (36–40%)
5. **Loại ngoại lệ khi báo cáo** — bulk orders làm lệch AOV và margin trung bình
6. **Điều tra sụt giảm đầu 2017** (~$21.2M, thấp hơn bình thường ~10%) — tìm nguyên nhân để phòng tránh
7. **Tối ưu sản phẩm đuôi** (bottom 20 sản phẩm không xuất hiện trong top) — cân nhắc cắt giảm danh mục hoặc cải thiện chi phí

---

## 10. Ứng dụng Web Gradio — Bảng Điều khiển Tương tác

### Tại sao cần ứng dụng Gradio (bên cạnh Power BI)?

Power BI yêu cầu Windows và cài Power BI Desktop — không chạy được trên macOS/Linux, không chia sẻ qua web mà không cần Power BI Pro (trả phí). Ứng dụng Gradio là ứng dụng web Python thuần, chạy mọi nơi, có thể đưa lên Hugging Face Spaces miễn phí.

---

### Thanh lọc toàn cục (Global Filter Bar) — Giải thích chi tiết

Đây là nhóm 4 bộ lọc nằm ở **đầu trang**, tác động đồng thời lên tất cả biểu đồ của cả 3 tab phân tích.

---

#### Bộ lọc Năm (Year Filter)

Cho phép chọn xem dữ liệu của **một hoặc nhiều năm** cụ thể: 2014, 2015, 2016, 2017.

- Mặc định: chọn tất cả các năm
- Ví dụ: chọn chỉ "2017" → tất cả biểu đồ chỉ hiển thị dữ liệu năm 2017, cho phép so sánh ngân sách kế hoạch vs. thực tế

---

#### Bộ lọc Kênh phân phối (Channel Filter)

**Kênh phân phối (Distribution Channel)** là con đường từ nhà sản xuất/nhà cung cấp đến người mua cuối cùng. Dữ liệu của Acme Co. có 3 kênh:

| Tên kênh | Tiếng Việt | Giải thích |
|---|---|---|
| **Wholesale** | Bán sỉ | Acme bán số lượng lớn cho các nhà bán lẻ hoặc đại lý. Đây là kênh chủ lực — chiếm **54%** tổng doanh thu. Đơn hàng lớn nhưng biên lợi nhuận thấp hơn vì phải chiết khấu giá sỉ. |
| **Distributor** | Nhà phân phối | Bán cho các nhà phân phối trung gian, họ sẽ tiếp tục bán lại cho thị trường. Chiếm **31%** doanh thu. |
| **Export** | Xuất khẩu | Bán ra thị trường nước ngoài. Chỉ chiếm **15%** doanh thu nhưng có **biên lợi nhuận cao nhất (37.93%)** vì không phải cạnh tranh về giá trong nước. |

Lọc theo kênh giúp trả lời: *"Kênh nào đang đóng góp nhiều nhất? Kênh nào cần đẩy mạnh?"*

---

#### Bộ lọc Vùng miền (US Region Filter)

**Vùng miền (US Region)** là cách phân chia địa lý nước Mỹ thành 4 khu vực lớn. Dữ liệu giao hàng của Acme Co. được phân theo 4 vùng:

| Tên vùng | Tiếng Việt | Các bang tiêu biểu | Đặc điểm trong dữ liệu |
|---|---|---|---|
| **West** | Vùng Tây | California, Washington, Oregon, Nevada | **Dẫn đầu ~$360M (~35%)** — thị trường lớn nhất, trưởng thành nhất |
| **South** | Vùng Nam | Texas, Florida, Georgia, North Carolina | Thị trường lớn thứ 2 |
| **Midwest** | Vùng Trung Tây | Illinois, Ohio, Michigan, Minnesota | Thị trường trung bình |
| **Northeast** | Vùng Đông Bắc | New York, Pennsylvania, Massachusetts | **Thấp nhất ~20%** — còn nhiều dư địa tăng trưởng chưa được khai thác |

Lọc theo vùng giúp trả lời: *"Vùng nào đang tăng trưởng tốt? Vùng nào cần đầu tư thêm?"*

---

#### Bộ lọc Sản phẩm (Product Filter)

Cho phép chọn **một hoặc nhiều sản phẩm** cụ thể từ 30 SKU (Product 1 → Product 30).
- Lựa chọn **"All Products"** (Tất cả sản phẩm) = không lọc, hiển thị toàn bộ danh mục
- Ví dụ: chọn "Product 26" → xem chi tiết hiệu suất của sản phẩm bán chạy nhất

---

### Kiến trúc luồng dữ liệu trong Gradio App

```
Thanh lọc toàn cục (Year / Channel / US Region / Product)
        |
        v  build_filter_state() — tính lại df_filtered
        |
   Trạng thái Gradio (gr.State)
        |
   +----+----+----+
   |    |    |    |
Tab1  Tab2  Tab3  Tab4
Tổng  Sản   Địa   Khám
quan  phẩm  lý    phá
      Kênh  KH    (PyGWalker)
```

---

### Tab 1 — Tổng quan (Overview)

Tab này trả lời câu hỏi: **"Tổng thể doanh nghiệp đang hoạt động như thế nào?"**

---

#### 5 Chỉ số Hiệu suất Chính (KPI — Key Performance Indicators)

**KPI** là những con số tóm tắt ngắn gọn nhất tình trạng của doanh nghiệp — giống như bảng đồng hồ trên xe hơi, cho thấy tốc độ, nhiên liệu, nhiệt độ... mà không cần xem toàn bộ động cơ.

---

**Tổng doanh thu (Total Revenue)**

Doanh thu (Revenue) là **tổng số tiền thu được từ việc bán hàng**, trước khi trừ bất kỳ chi phí nào.

```
Doanh thu = Số lượng × Đơn giá
Revenue   = Quantity × Unit Price
```

Ví dụ: bán 100 sản phẩm với giá $500/cái → Doanh thu = $50,000

Tổng doanh thu toàn dự án: **~$1.24 tỷ USD** (2014–2017)

> Doanh thu cao không có nghĩa là lời nhiều — cần xem thêm Lợi nhuận (Profit) để biết thực sự kiếm được bao nhiêu sau khi trừ chi phí.

---

**Tổng lợi nhuận (Total Profit)**

Lợi nhuận (Profit) là **số tiền còn lại sau khi trừ đi tất cả chi phí** để tạo ra sản phẩm đó.

```
Lợi nhuận = Doanh thu − Tổng chi phí
Profit     = Revenue   − Total Cost
           = Revenue   − (Quantity × Unit Cost)
```

Ví dụ: Doanh thu $50,000, Chi phí $31,500 → Lợi nhuận = $18,500

> Đây là số tiền "thật sự kiếm được" — quan trọng hơn doanh thu khi đánh giá hiệu quả kinh doanh.

---

**Biên lợi nhuận (Profit Margin)**

Biên lợi nhuận (Profit Margin) là **tỷ lệ phần trăm lợi nhuận trên doanh thu** — cho biết cứ $100 doanh thu thì doanh nghiệp giữ lại được bao nhiêu đồng lợi nhuận.

```
Biên lợi nhuận (%) = (Lợi nhuận / Doanh thu) × 100
Profit Margin (%)   = (Profit / Revenue) × 100
```

Ví dụ: Doanh thu $50,000, Lợi nhuận $18,500 → Biên lợi nhuận = 37%

Trong dự án này: biên lợi nhuận trung bình **~37%** — nghĩa là cứ $100 thu vào, Acme Co. giữ lại ~$37 lợi nhuận.

> Biên lợi nhuận 37% là **mức cao** trong ngành phân phối. Kênh Export có biên lợi nhuận 37.93% — cao nhất trong 3 kênh.

---

**Tổng số đơn hàng (Total Orders)**

Đếm số lượng đơn hàng **duy nhất** (unique) trong dữ liệu đã lọc — mỗi mã đơn hàng (order_number) được đếm một lần.

```
Tổng đơn hàng = Số lượng order_number duy nhất
Total Orders  = COUNT(DISTINCT order_number)
```

Chỉ số này cho biết **khối lượng giao dịch** của doanh nghiệp — bao nhiêu lần khách hàng đặt mua hàng.

---

**Doanh thu trên mỗi đơn hàng (Revenue per Order)**

Còn gọi là **Giá trị đơn hàng trung bình (AOV — Average Order Value)**. Đây là số tiền trung bình của một đơn hàng.

```
Doanh thu / Đơn hàng = Tổng doanh thu / Tổng số đơn hàng
Revenue per Order    = Total Revenue / Total Orders
```

Ví dụ: Tổng doanh thu $1.24 tỷ, 64,104 đơn hàng → Revenue per Order ≈ **$19,000/đơn**

> Nếu Revenue per Order tăng theo thời gian → khách hàng đang mua nhiều hơn mỗi lần đặt hàng (upsell hiệu quả). Nếu giảm → có thể đang mất khách hàng lớn.

---

#### Biểu đồ 1 — Xu hướng Doanh thu Hàng tháng (Monthly Revenue Trend)

Biểu đồ này có **2 chế độ xem** chuyển đổi bằng nút Radio:

---

**Chế độ Chuỗi thời gian (Timeseries)**

Hiển thị doanh thu **theo từng tháng cụ thể** trên trục thời gian liên tục từ đầu đến cuối.

```
Trục X: Tháng–Năm (ví dụ: Jan 2014, Feb 2014, ..., Dec 2017)
Trục Y: Tổng doanh thu (USD)
```

**Dùng để làm gì:**
- Thấy được **xu hướng tổng thể** qua nhiều năm (doanh thu có tăng dần không?)
- Phát hiện **các tháng bất thường** (tăng đột ngột hoặc giảm mạnh)
- So sánh **cùng tháng qua các năm** khác nhau (tháng 12/2014 vs tháng 12/2015)

**Insight từ dữ liệu Acme Co.:** Doanh thu ổn định ở mức $23–26M/tháng, không có xu hướng tăng mạnh theo năm, không có sụt giảm đột ngột.

---

**Chế độ Mùa vụ (Seasonal)**

Gộp dữ liệu của **tất cả các năm lại**, tính trung bình doanh thu theo từng tháng trong năm (tháng 1 → tháng 12).

```
Trục X: Tháng trong năm (January → December)
Trục Y: Doanh thu trung bình của tháng đó (qua tất cả các năm)
```

**Dùng để làm gì:**
- Trả lời câu hỏi: **"Tháng nào trong năm thường bán chạy nhất?"**
- Lập kế hoạch tồn kho và marketing theo mùa vụ
- Phát hiện quy luật lặp đi lặp lại hàng năm (seasonality pattern)

**Insight từ dữ liệu Acme Co.:** Tháng 5 là đỉnh cao nhất (~$102M khi gộp), tháng 1 là đáy thấp nhất. → Nên tăng ngân sách marketing trước tháng 5, giảm tháng 1.

---

#### Biểu đồ 2 — Xu hướng Lợi nhuận Hàng tháng (Monthly Profit Trend)

Tương tự biểu đồ doanh thu nhưng theo dõi **lợi nhuận** thay vì doanh thu.

```
Trục X: Tháng–Năm
Trục Y: Tổng lợi nhuận (USD)
```

**Dùng để làm gì:**
- Kiểm tra xem doanh thu và lợi nhuận có **tăng giảm cùng nhau** không (tương quan 0.87 → thường là có)
- Phát hiện các tháng doanh thu cao nhưng lợi nhuận thấp — có thể đang bán giảm giá quá nhiều hoặc chi phí tăng
- Theo dõi **sức khoẻ thực sự** của doanh nghiệp (không chỉ nhìn doanh thu)

---

#### Biểu đồ 3 — Phân phối Giá trị Đơn hàng (Order Value Distribution — Histogram)

Biểu đồ tần suất (Histogram) chia toàn bộ đơn hàng thành các khoảng giá trị (bins) và đếm xem bao nhiêu đơn hàng rơi vào mỗi khoảng.

```
Trục X: Giá trị đơn hàng (USD) — chia thành 50 khoảng đều nhau
Trục Y: Số lượng đơn hàng trong khoảng đó
```

**Dùng để làm gì:**
- Hiểu **đơn hàng điển hình** của Acme Co. trị giá bao nhiêu
- Phát hiện **đơn hàng cực lớn (outliers)** — các bulk orders bất thường
- Hỗ trợ quyết định về **chính sách chiết khấu** (discount policy) cho từng mức giá trị đơn hàng

**Insight:** Phân phối lệch phải (right-skewed) — phần lớn đơn hàng tập trung ở $50–60K, nhưng có một số đơn cực lớn kéo giá trị trung bình lên cao. → Cần loại outliers khi tính trung bình để có con số chính xác hơn.

---

#### Biểu đồ 4 — Doanh thu & Lợi nhuận theo Kênh (Revenue & Profit by Channel)

Biểu đồ thanh nhóm (Grouped Bar Chart) — mỗi kênh có 2 cột đặt cạnh nhau: Doanh thu (xanh dương) và Lợi nhuận (xanh lá).

```
Trục X: 3 kênh phân phối (Wholesale / Distributor / Export)
Trục Y: Giá trị USD
Màu xanh dương: Tổng doanh thu (Revenue)
Màu xanh lá: Tổng lợi nhuận (Profit)
```

**Dùng để làm gì:**
- So sánh **doanh thu vs. lợi nhuận** của từng kênh trong cùng một biểu đồ
- Thấy ngay kênh nào có **khoảng cách lớn giữa doanh thu và lợi nhuận** (chi phí cao)
- Đưa ra quyết định: nên ưu tiên kênh có doanh thu lớn hay kênh có lợi nhuận cao?

**Insight:** Wholesale có doanh thu lớn nhất nhưng khoảng cách với lợi nhuận cũng lớn (phải bán sỉ với giá chiết khấu cao). Export có doanh thu thấp nhất nhưng khoảng cách hẹp hơn (biên lợi nhuận tốt hơn).

---

#### Ô nhận xét tự động (Rule-based Insight)

Ngay bên dưới 4 biểu đồ, ô nhận xét màu xanh nhạt **tự động cập nhật** mỗi khi lọc thay đổi, tóm tắt 3 điểm chính:
- Tổng doanh thu, số đơn hàng, biên lợi nhuận
- Tháng có doanh thu cao nhất
- Giá trị trung bình mỗi đơn hàng

#### Nút Khuyến nghị AI (AI Recommendation Button)

Nhấn nút → ứng dụng gọi OpenAI `gpt-4o-mini`, gửi tóm tắt dữ liệu hiện tại và nhận về **3–5 khuyến nghị chiến lược bằng tiếng Việt**, kèm số liệu cụ thể từ dữ liệu thực.

---

### Tab 2 — Sản phẩm & Kênh phân phối (Product & Channel)

Tab này trả lời: **"Sản phẩm nào bán tốt? Kênh nào hiệu quả?"**

---

**Biểu đồ 1 — Top 10 sản phẩm theo Doanh thu (Top 10 Products by Revenue)**

Biểu đồ thanh nằm ngang, sắp xếp 10 sản phẩm có doanh thu cao nhất từ trên xuống dưới.

**Dùng để làm gì:** Xác định các sản phẩm **"ngôi sao"** đang tạo ra phần lớn doanh thu. Trong kinh doanh, thường 20% sản phẩm tạo ra 80% doanh thu (quy tắc Pareto).

**Insight:** Product 26 dẫn đầu với ~$118M — đây là sản phẩm cần được ưu tiên đảm bảo tồn kho đầy đủ.

---

**Biểu đồ 2 — Top 10 sản phẩm theo Lợi nhuận trung bình (Top 10 Products by Avg Profit)**

Biểu đồ thanh nằm ngang, xếp hạng theo **lợi nhuận trung bình mỗi giao dịch**, không phải tổng.

**Dùng để làm gì:** Tìm sản phẩm **có biên lợi nhuận cao** — không phải sản phẩm bán nhiều nhất mà là sản phẩm "lời nhất" mỗi lần bán. Đây là căn cứ để quyết định sản phẩm nào nên được ưu tiên trong chiến dịch marketing.

---

**Biểu đồ 3 — Tỷ lệ Doanh thu theo Kênh (Revenue Share by Channel — Donut Chart)**

Biểu đồ tròn rỗng giữa (Donut Chart) thể hiện tỷ lệ phần trăm đóng góp doanh thu của mỗi kênh.

**Dùng để làm gì:** Nhìn một cái là thấy ngay kênh nào **chiếm ưu thế** và kênh nào đang bị lép vế trong cơ cấu doanh thu.

---

**Biểu đồ 4 — Biên lợi nhuận trung bình theo Kênh (Avg Profit Margin % by Channel)**

Biểu đồ thanh đứng, so sánh **biên lợi nhuận trung bình** của 3 kênh.

**Dùng để làm gì:** Kết hợp với biểu đồ tỷ lệ doanh thu để ra quyết định chiến lược: *"Kênh Export có margin cao nhất nhưng doanh thu thấp nhất — đây là cơ hội tăng trưởng lớn nếu mở rộng thị trường xuất khẩu."*

---

**Biểu đồ 5 — Phân phối Đơn giá từng Sản phẩm (Unit Price Distribution — Box Plot)**

Biểu đồ hộp (Box Plot) — mỗi sản phẩm có một hộp thể hiện phân phối giá: giá nhỏ nhất, phần tư thứ nhất (Q1), trung vị (Median), phần tư thứ ba (Q3), giá lớn nhất, và các điểm ngoại lệ (outliers).

**Dùng để làm gì:** Tìm sản phẩm có **giá bán dao động lớn** (hộp dài) — có thể do chiết khấu không nhất quán giữa các kênh hoặc theo thời gian.

---

### Tab 3 — Địa lý & Khách hàng (Geography & Customer)

Tab này trả lời: **"Thị trường nào mạnh? Khách hàng nào quan trọng?"**

---

**Biểu đồ 1 — Doanh thu theo Vùng miền (Revenue by US Region)**

Biểu đồ thanh nằm ngang, so sánh tổng doanh thu của 4 vùng địa lý.

**Dùng để làm gì:** Xác định **vùng trọng tâm** và **vùng cần đầu tư thêm**.

---

**Biểu đồ 2 — Bản đồ Doanh thu theo Bang (Revenue by State — Choropleth Map)**

Bản đồ tô màu nước Mỹ — bang nào có doanh thu cao thì màu xanh đậm hơn.

**Dùng để làm gì:**
- Nhìn trực quan toàn bộ nước Mỹ, thấy ngay **"vùng nóng"** và **"vùng lạnh"**
- Phát hiện cụm (cluster) các bang liền kề có hiệu suất tốt → có thể mở thêm kho/nhà phân phối khu vực đó

**Insight:** California chiếm ~$230M — đậm nhất trên bản đồ. Các bang miền Đông Bắc (Northeast) có màu nhạt → thị trường chưa được khai thác.

---

**Biểu đồ 3 — Top 10 Bang: Doanh thu & Đơn hàng (Top States — Dual Bar)**

Biểu đồ thanh kép (Dual-axis Bar Chart) — 2 trục Y khác nhau: một cho Doanh thu (USD), một cho Số đơn hàng (Orders).

**Dùng để làm gì:** So sánh 2 chiều cùng lúc — bang nào có **doanh thu lớn nhưng ít đơn** (đơn hàng giá trị cao) vs. bang có **nhiều đơn nhưng doanh thu thấp** (đơn hàng nhỏ lẻ).

---

**Biểu đồ 4 — Top/Bottom Khách hàng theo Doanh thu (Customer Bar Chart)**

Biểu đồ thanh nằm ngang, có **nút Radio chuyển đổi** giữa 2 chế độ:

- **Top 10**: 10 khách hàng đóng góp doanh thu **cao nhất** — đây là nhóm cần được chăm sóc đặc biệt, ưu tiên giữ chân (retention)
- **Bottom 10**: 10 khách hàng đóng góp doanh thu **thấp nhất** — nhóm này có thể cần chiến lược kích hoạt lại (re-engagement) hoặc hiểu tại sao họ mua ít

**Insight:** Aibox Co. dẫn đầu với ~$12.5M — gấp nhiều lần khách hàng trung bình.

---

**Biểu đồ 5 — Phân khúc Khách hàng (Customer Segmentation — Bubble Chart)**

Biểu đồ bong bóng (Bubble Chart) — mỗi bong bóng là một khách hàng:
- Trục X: Tổng doanh thu (Total Revenue) của khách hàng
- Trục Y: Biên lợi nhuận trung bình (Avg Profit Margin %)
- Kích thước bong bóng: Số đơn hàng (Number of Orders)

**Dùng để làm gì:** Phân nhóm khách hàng theo 3 chiều cùng lúc, xác định:
- **Khách hàng vàng (High-value)**: bong bóng lớn, nằm góc trên phải — doanh thu cao + margin cao + nhiều đơn
- **Khách hàng tiềm năng**: margin cao nhưng doanh thu còn thấp — có thể upsell thêm
- **Khách hàng cần xem lại**: doanh thu lớn nhưng margin thấp — đang bán quá rẻ

---

**Biểu đồ 6 — Ma trận Tương quan (Correlation Heatmap)**

Bản đồ nhiệt (Heatmap) thể hiện **mức độ tương quan** giữa 5 biến số: số lượng (quantity), đơn giá (unit_price), doanh thu (revenue), chi phí (cost), lợi nhuận (profit).

```
Tương quan = 1.0  → khi biến A tăng, biến B luôn tăng theo (hoàn toàn cùng chiều)
Tương quan = 0.0  → biến A và B không liên quan gì đến nhau
Tương quan = -1.0 → khi biến A tăng, biến B luôn giảm (hoàn toàn ngược chiều)
```

**Dùng để làm gì:**
- Kiểm tra xem **tăng doanh thu có tự động tăng lợi nhuận** không (Profit–Revenue: 0.87 → có, rất mạnh)
- Biết **số lượng đơn hàng** có ảnh hưởng đến lợi nhuận không (tương quan yếu → không đáng kể)
- Tránh đưa vào mô hình 2 biến **quá tương quan** với nhau (sẽ gây nhiễu phân tích)

---

### Tab 4 — Khám phá Dữ liệu (Explorer — PyGWalker)

Tab này dùng thư viện **PyGWalker** để tạo một giao diện **kéo-thả tương tác** (drag-and-drop) giống Tableau.

**Cách dùng:**
1. Kéo một cột từ danh sách vào ô **Dimension** (chiều phân tích — ví dụ: product_name, channel, us_region)
2. Kéo một cột số vào ô **Measure** (phép đo — ví dụ: revenue, profit, quantity)
3. PyGWalker tự động vẽ biểu đồ phù hợp
4. Có thể thêm **màu sắc, kích thước, bộ lọc** riêng

**Dùng để làm gì:** Khám phá tự do các câu hỏi ad-hoc mà 3 tab kia chưa có sẵn biểu đồ — ví dụ: "Doanh thu theo kênh phân theo từng bang cụ thể thì sao?"

---

### Kiến trúc phần mềm và Testing (Kiểm thử)

**38 bài kiểm thử tự động (pytest)** đã pass — đảm bảo ứng dụng hoạt động đúng:
- `tests/test_data.py` (9): tải CSV, áp dụng lọc từng chiều
- `tests/test_charts.py` (18): kiểm thử mỗi hàm vẽ biểu đồ với df rỗng và df có dữ liệu
- `tests/test_insights.py` (7): kiểm thử nhận xét tự động, LLM mock, df rỗng
- `tests/test_kpis.py` (4): kiểm thử độ chính xác của `compute_kpis()`

---

## 11. Hướng dẫn Cài đặt và Chạy dự án

### Phần A — Chạy Sổ ghi chép Jupyter (EDA + Xuất CSV)

**Yêu cầu:** Python 3.8+, pandas, numpy, matplotlib, seaborn, Google Colab hoặc Jupyter Notebook

**Bước 1:** Chuẩn bị file dữ liệu
```
Tải file Regional Sales Dataset.xlsx
Nếu dùng Google Colab: upload lên Google Drive
Nếu dùng Jupyter local: đặt file vào thư mục dự án
```

**Bước 2:** Mở sổ ghi chép
```
Mở EDA_Regional_Sales_Analysis.ipynb trong Google Colab hoặc Jupyter
```

**Bước 3:** Sửa đường dẫn (Cell 10)
```python
# Nếu chạy trên Google Colab:
from google.colab import drive
drive.mount('/content/drive')
file_path = '/content/drive/MyDrive/path/to/Regional Sales Dataset.xlsx'

# Nếu chạy Jupyter local (xoá 2 dòng google.colab và sửa):
file_path = './Regional Sales Dataset.xlsx'
```

**Bước 4:** Chạy tất cả ô lệnh (cells) theo thứ tự từ đầu đến cuối

**Bước 5:** Kiểm tra kết quả
- DataFrame cuối cùng có **21 cột và 64,104 bản ghi**
- Tất cả **15 biểu đồ** hiển thị đúng
- Cell 75 tạo thành công file `Sales_data(EDA Exported).csv`

---

### Phần B — Xem Bảng điều khiển Power BI (Power BI Dashboard)

**Yêu cầu:** Microsoft Power BI Desktop (chỉ hỗ trợ Windows, tải miễn phí)

**Bước 1:** Đảm bảo file `Sales_data(EDA Exported).csv` đã được tạo từ Phần A

**Bước 2:** Mở file `SALES REPORT.pbix` trong Power BI Desktop

**Bước 3:** Nếu dữ liệu không tải được, đổi nguồn dữ liệu (data source):
`Home → Transform Data → Data Source Settings → Change Source`
Trỏ đến đúng đường dẫn file CSV trên máy bạn

**Bước 4:** Nhấn `Refresh` để tải dữ liệu mới nhất

---

### Phần C — Chạy Ứng dụng Web Gradio (Khuyến nghị)

**Yêu cầu:** Python 3.10+, công cụ quản lý gói `uv`

**Bước 1:** Cài `uv` (nếu chưa có)
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**Bước 2:** Di chuyển vào thư mục dự án
```bash
cd "/path/to/Regional Sales Summary"
```

**Bước 3:** Cài đặt tất cả thư viện phụ thuộc
```bash
uv sync
```

**Bước 4:** (Tuỳ chọn) Cấu hình khoá API OpenAI để dùng tính năng AI
```bash
cp .env.example .env
# Mở file .env và điền: OPENAI_API_KEY=sk-...
```

**Bước 5:** Khởi chạy ứng dụng
```bash
uv run python app.py
```
Ứng dụng tự động mở tại `http://localhost:7860`

**Bước 6:** Kiểm tra trước khi demo
```bash
uv run pytest -v           # kỳ vọng: 38 passed
uv run python -c "from app import build_app; build_app(); print('OK')"
```

---

## 12. Kết quả đạt được

### Sản phẩm cuối cùng

| Sản phẩm | Đặc điểm nổi bật |
|---|---|
| Dữ liệu đã xử lý | 64,104 bản ghi × 21 cột, sạch, sẵn sàng cho mọi công cụ phân tích |
| Sổ ghi chép EDA (EDA Notebook) | 15 phân tích, 15 biểu đồ, nhận xét và khuyến nghị kinh doanh |
| Bảng điều khiển Power BI | 3 trang, điều hướng, thẻ đánh dấu (bookmarks), phép đo DAX, nền Canva |
| Ứng dụng Web Gradio | 4 tab, 16 biểu đồ Plotly, 3 nút AI, PyGWalker explorer, 38 bài kiểm thử pass |

### Những phát hiện chính (Key Findings)

- Tổng doanh thu **~$1.24 tỷ USD** qua 4 năm 2014–2017
- Biên lợi nhuận trung bình **~37%** — ổn định trên toàn danh mục
- **Wholesale** là kênh chủ lực (54% doanh thu) nhưng **Export** có biên lợi nhuận cao nhất (37.93%)
- **California** chiếm gần $230M — gấp đôi bang thứ 2 (Texas)
- **Vùng West** ~35% tổng doanh thu; **Vùng Northeast** còn nhiều dư địa
- Tháng **5** là đỉnh cao nhất (khi gộp tất cả năm); tháng 1 là đáy thấp nhất
- Khách hàng lớn nhất (**Aibox Co. ~$12.5M**) vẫn duy trì biên lợi nhuận tốt — quy mô không làm giảm lợi nhuận
- Lợi nhuận–Doanh thu tương quan **0.87** — tăng doanh thu trực tiếp cải thiện lợi nhuận

### Khuyến nghị chiến lược tổng hợp

1. **Mở rộng kênh Export** — biên lợi nhuận cao nhất (37.93%) nhưng còn thấp (15% doanh thu)
2. **Đầu tư vào Vùng Northeast** — thị trường chưa bão hoà, tiềm năng tăng trưởng lớn
3. **Tập trung marketing tháng 4–5** — đỉnh mùa vụ, cần đảm bảo tồn kho và năng lực giao hàng
4. **Giữ chân Top 10 khách hàng** — chiếm tỷ trọng doanh thu lớn, biên lợi nhuận tốt
5. **Tối ưu sản phẩm có biên lợi nhuận thấp** — cắt giảm chi phí hoặc điều chỉnh giá bán

---

## 13. Kiến thức và Kỹ năng thể hiện

| Lĩnh vực | Kỹ năng cụ thể |
|---|---|
| Python / pandas | Đọc Excel nhiều trang tính (read_excel), hợp nhất bảng (merge — left join), nhóm dữ liệu (groupby), xây dựng đặc trưng (Feature Engineering), chuyển đổi kiểu ngày tháng (datetime parsing) |
| Mô hình hoá Dữ liệu (Data Modeling) | Sơ đồ thực thể quan hệ (ERD), Khoá chính/Khoá ngoại (Primary/Foreign Key), Bảng sự kiện/Bảng chiều (Fact/Dimension Table), Lược đồ hình sao (Star Schema) |
| Phân tích Khám phá Dữ liệu (EDA) | Đơn biến (Univariate), Song biến (Bivariate), Đa biến (Multivariate), Phân tích thời gian (Temporal), Không gian địa lý (Geospatial) |
| Trực quan hoá | matplotlib, seaborn (sổ ghi chép), Biểu đồ tương tác Plotly (ứng dụng Gradio) |
| Power BI | Phép đo DAX (DAX Measures), Điều hướng trang (Page Navigation), Thẻ đánh dấu (Bookmarks), Bộ lọc (Slicers), Hình nền Canva (Canvas Background) |
| Kỹ thuật phần mềm | Kiến trúc mô-đun (Modular Architecture), Phát triển hướng kiểm thử (TDD — Test-Driven Development, pytest 38 bài kiểm thử), mã sạch (clean code) |
| Gradio 6.x | Blocks, Quản lý trạng thái (State Management), Chuỗi sự kiện (Event Chaining), Tích hợp PyGWalker |
| AI / Mô hình Ngôn ngữ Lớn (LLM) | Giao tiếp OpenAI API, Kỹ thuật viết câu lệnh (Prompt Engineering), Xử lý lỗi khi không có khoá API (Graceful Degradation) |
| Quản lý môi trường | Công cụ quản lý gói uv, pyproject.toml, biến môi trường .env, .gitignore |

---

*Tài liệu này tổng hợp từ: nội dung bài giảng 325–328 (Summary.txt), tài liệu dự án (USA_Regional_Sales_Analysis_Project_Documentation.txt), toàn bộ mã nguồn ứng dụng Gradio, và sổ ghi chép EDA.*
