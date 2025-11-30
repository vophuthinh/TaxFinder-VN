# Masothue - Tra cứu Mã số thuế

Ứng dụng desktop hiện đại để tra cứu thông tin doanh nghiệp theo mã số thuế hoặc tên công ty từ website masothue.com. Hỗ trợ tra cứu đơn lẻ và tra cứu hàng loạt từ file Excel với giao diện chuyên nghiệp, tính năng caching thông minh và thread-safe architecture.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-Research%20Only-yellow.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)

## ✨ Tính năng

### 🎨 Giao diện

- **Header bar chuyên nghiệp**: Header bar màu đen với title và subtitle
- **Menu bar đầy đủ**: Menu "Cài đặt" và "Trợ giúp" với các chức năng hữu ích
- **UI hiện đại**: Giao diện đẹp mắt với màu sắc chuyên nghiệp, font Segoe UI
- **Empty state**: Hiển thị thông báo rõ ràng khi chưa có dữ liệu
- **Zebra rows**: Bảng kết quả có màu xen kẽ dễ đọc
- **Panel chi tiết**: Hiển thị thông tin chi tiết bên phải khi chọn dòng
- **Auto-select**: Tự động chọn dòng đầu tiên khi có kết quả
- **ETL Loading Indicator**: Card loading với progress bar và nút Hủy tích hợp
- **Responsive layout**: Layout linh hoạt với PanedWindow, tự điều chỉnh theo DPI
- **UI Locking**: Tự động khóa UI khi đang batch để tránh conflict
- **Input validation feedback**: Hiển thị trạng thái khi nhập MST hoặc text dài

### 🔍 Tra cứu

- **Tra cứu đơn lẻ**: Tìm kiếm công ty theo tên hoặc mã số thuế
- **Tra cứu hàng loạt**: Nhập file Excel và tra cứu nhiều công ty cùng lúc
- **Kết quả chính xác**: Tự động tìm kết quả khớp chính xác khi tra cứu bằng MST
- **Fetch details**: Tự động lấy thông tin chi tiết đầy đủ
- **Input validation**: Tự động validate và sanitize input trước khi tra cứu

### 💾 Dữ liệu

- **Import Excel**: Đọc danh sách công ty từ file Excel (.xlsx, .xls)
  - Tự động nhận diện cột chứa MST hoặc tên công ty
  - Validate MST linh hoạt (8-15 chữ số)
  - Loại bỏ trùng lặp tự động
- **Export Excel**: Xuất kết quả tra cứu ra file Excel với metadata
- **Cache thông minh**: 
  - Tự động cache kết quả để tăng tốc độ tra cứu lần sau
  - Cache size limit (mặc định 100MB)
  - Tự động cleanup cache cũ và vượt quá size limit
  - Thread-safe cache operations

### ⚙️ Cài đặt nâng cao

- **Dialog cài đặt**: Menu "Cài đặt → Cài đặt nâng cao..."
  - Rate limiting: max_requests, time_window, min_delay
  - Cache: bật/tắt cache, cache_expiry_days
  - Nút "Đặt lại mặc định" và "Áp dụng"

### ⚡ Hiệu năng & Bảo mật

- **Rate limiting**: Tự động giới hạn số lượng request, random delay
- **Thread-safe**: Tất cả operations đều thread-safe với `threading.Lock()`
- **Optimized parsing**: Tránh double parsing HTML (parse một lần, dùng lại)
- **Caching**: Cache kết quả theo MST, hết hạn sau 7 ngày (có thể config)
- **CAPTCHA Detection**: Phát hiện CAPTCHA chính xác bằng BeautifulSoup

## 📋 Thông tin lấy được

Khi tra cứu, ứng dụng sẽ lấy các thông tin sau:

- ✅ **Mã số thuế**
- ✅ **Tên công ty**
- ✅ **Địa chỉ Thuế**
- ✅ **Địa chỉ**
- ✅ **Người đại diện**
- ✅ **Điện thoại**
- ✅ **Tình trạng** (Đang hoạt động/Ngừng hoạt động)
- ✅ **Ngày hoạt động**
- ✅ **Quản lý bởi**
- ✅ **Loại hình DN**
- ✅ **Ngành nghề chính**
- ✅ **Ngành nghề khác**
- ✅ **URL chi tiết** (double-click để mở)

## 🚀 Cài đặt

### Yêu cầu

- Python 3.11 trở lên
- pip (Python package manager)

### Các bước cài đặt

1. **Clone hoặc download dự án**

```bash
git clone <repository-url>
cd Masothue
```

2. **Cài đặt dependencies**

```bash
pip install -r requirements.txt
```

3. **Chạy ứng dụng GUI**

```bash
python main.py
```

Hoặc trên Windows:

```bash
run.bat
```

## 📖 Hướng dẫn sử dụng

### GUI Application

#### Tra cứu đơn lẻ

1. Mở ứng dụng
2. Nhập tên công ty hoặc mã số thuế vào ô tìm kiếm
3. Nhấn nút **"🔎 Tra cứu"** hoặc nhấn Enter
4. Kết quả sẽ hiển thị trong bảng bên trái
5. Click vào một dòng để xem thông tin chi tiết bên phải
6. Double-click vào dòng để mở trang chi tiết trên web

#### Tra cứu hàng loạt từ Excel

1. Chuẩn bị file Excel với cột chứa tên công ty hoặc mã số thuế
2. Nhấn nút **"📥 Nhập Excel"**
3. Chọn file Excel của bạn
4. Xác nhận số lượng công ty cần tra cứu
5. Chờ quá trình tra cứu hoàn tất
6. Có thể nhấn **"✕ Hủy"** để dừng quá trình bất cứ lúc nào
7. Xem kết quả trong bảng hoặc nhấn **"📤 Xuất Excel"** để lưu ra file mới

### Command Line Interface (CLI)

Ứng dụng cũng hỗ trợ CLI để tra cứu từ terminal:

#### Tra cứu đơn lẻ

```bash
python -m masothue.cli search --query "3604062974"
python -m masothue.cli search --query "Công ty ABC"
python -m masothue.cli search --query "3604062974" --verbose
```

#### Tra cứu hàng loạt

```bash
python -m masothue.cli batch input.xlsx output.xlsx
python -m masothue.cli batch input.xlsx  # Tự động tạo output file
python -m masothue.cli batch input.xlsx output.xlsx --verbose
```

## 📁 Cấu trúc dự án

```
Masothue/
├── main.py                    # Entry point cho GUI application
├── masothue_app.py            # Ứng dụng GUI (Tkinter)
├── masothue/                  # Package chính
│   ├── __init__.py           # Package exports
│   ├── client.py             # MasothueClient - Core logic (thread-safe, optimized parsing)
│   ├── models.py            # CompanySearchResult dataclass
│   ├── cache.py             # FileCache - Caching system (thread-safe, size limit)
│   ├── rate_limiter.py      # RateLimiter - Rate limiting (thread-safe, metrics)
│   ├── batch_worker.py      # BatchWorker - Batch processing logic
│   ├── excel_service.py     # ExcelService - Excel I/O operations
│   ├── formatters.py        # Data formatting utilities
│   ├── config.py            # Cấu hình package
│   ├── constants.py         # UI constants và messages
│   ├── theme.py             # Theme colors
│   ├── exceptions.py        # Custom exceptions hierarchy
│   ├── utils.py             # Utility functions (validation, sanitization)
│   └── cli.py               # Command-line interface
├── views/                    # UI view components (optional)
│   ├── search_frame.py
│   └── batch_frame.py
├── requirements.txt          # Dependencies
├── README.md                 # File này
├── logs/                     # Thư mục log files (tự động tạo)
│   └── masothue_YYYYMMDD.log
└── .cache/                   # Thư mục cache (tự động tạo)
```

## 💻 Sử dụng như một Package

Bạn có thể import và sử dụng `masothue` như một Python package:

```python
from masothue import (
    MasothueClient, 
    CompanySearchResult,
    CaptchaRequiredError,
    NetworkError,
    ValidationError,
    FileError
)

# Tạo client
client = MasothueClient(
    max_requests=10,
    time_window=60,
    min_delay=1.0,
    enable_cache=True,
    cache_dir=".cache",
    cache_expiry_days=7
)

# Tra cứu đơn lẻ
try:
    results = client.search_companies("3604062974")
    for result in results:
        print(f"{result.name} - {result.tax_code}")
        
    # Lấy chi tiết
    if results and results[0].detail_url:
        details = client.get_company_details(results[0].detail_url)
        print(details)
        
except CaptchaRequiredError:
    print("Website yêu cầu CAPTCHA")
except NetworkError as e:
    print(f"Lỗi mạng: {e}")
except ValidationError as e:
    print(f"Dữ liệu không hợp lệ: {e}")

# Xem metrics của rate limiter
metrics = client.rate_limiter.get_metrics()
print(f"Requests/second: {metrics['requests_per_second']}")
print(f"Average delay: {metrics['average_delay']}s")

# Cleanup cache
stats = client.file_cache.prune()
print(f"Đã xóa {stats['deleted_count']} file cache, giải phóng {stats['freed_mb']:.2f}MB")
```

## ⚙️ Cấu hình

### Cấu hình ứng dụng (config.py)

Bạn có thể chỉnh sửa các thông số trong file `masothue/config.py`:

```python
BASE_URL = "https://masothue.com"

DEFAULT_RATE_LIMIT = {
    "max_requests": 10,      # Số request tối đa trong time_window
    "time_window": 60,       # Khoảng thời gian tính bằng giây
    "min_delay": 1.0,        # Delay tối thiểu giữa các request (giây)
    "max_delay": 3.0,        # Delay tối đa (random delay để tránh pattern)
    "use_random_delay": True # Sử dụng random delay giữa min_delay và max_delay
}

REQUEST_TIMEOUT = 8          # Timeout cho mỗi request (giây)
REQUEST_RETRIES = 2          # Số lần retry khi lỗi
REQUEST_RETRY_DELAY = 1      # Delay giữa các retry (giây)

# Cache settings
CACHE_ENABLED = True         # Bật/tắt cache
CACHE_DIR = ".cache"         # Thư mục lưu cache
CACHE_EXPIRY_DAYS = 7        # Cache hết hạn sau bao nhiêu ngày
CACHE_MAX_SIZE_MB = 100.0    # Kích thước cache tối đa (MB)
CACHE_ENABLE_CLEANUP = True  # Tự động cleanup cache khi vượt quá size limit
```

### Cấu hình từ UI

Bạn có thể cấu hình rate limiting và cache trực tiếp từ giao diện:

1. Mở menu **"Cài đặt → Cài đặt nâng cao..."**
2. Điều chỉnh các thông số
3. Nhấn **"Áp dụng"** để lưu cài đặt

## 📦 Dependencies

- `requests` - HTTP library để gửi requests
- `beautifulsoup4` - Parse HTML (cải thiện CAPTCHA detection)
- `openpyxl` - Đọc/ghi file Excel
- `python-dotenv` - Load environment variables (nếu cần)

Xem chi tiết trong `requirements.txt`

## 🔧 Tính năng kỹ thuật

### Rate Limiting
- Tự động giới hạn số lượng request trong một khoảng thời gian
- Tránh bị website chặn do spam request
- **Thread-safe** với `threading.Lock()`
- **Random delay** giữa các request để giảm pattern detection
- **Metrics tracking**: `get_metrics()` để lấy thống kê

### Retry Logic
- Tự động retry khi gặp lỗi mạng
- Exponential backoff: delay tăng dần sau mỗi lần retry
- Xử lý riêng cho HTTP 404 (không retry)
- Xử lý riêng cho CAPTCHA (không retry, raise exception ngay)

### Caching System
- **File-based cache**: Lưu cache vào disk trong thư mục `.cache/`
- **Cache key**: Sử dụng MST hoặc hash của URL
- **Expiry**: Cache tự động hết hạn sau N ngày
- **Size limit**: Tự động cleanup khi vượt quá size limit
- **Thread-safe**: File operations được bảo vệ bằng `threading.Lock()`

### Threading & UI Updates
- Tra cứu đơn lẻ và hàng loạt đều chạy trong thread riêng
- UI không bị lag khi tra cứu
- **Thread-safe với queue.Queue**: Tất cả UI updates từ background threads đều qua queue
- **Thread-safe network**: `requests.Session` và `RateLimiter` được bảo vệ bằng `threading.Lock()`
- **UI Locking**: Tự động khóa các nút UI khi đang batch

### HTML Parsing Optimization
- **Tránh double parsing**: Parse HTML một lần trong `_get_html_and_soup()`, dùng lại soup cho CAPTCHA check và data extraction
- Sử dụng **BeautifulSoup** để parse HTML chính xác
- Kết hợp text search và cấu trúc HTML (table, itemprop, etc.)
- Có fallback mechanisms khi website thay đổi

### CAPTCHA Detection
- **Phát hiện chính xác**: Chỉ báo CAPTCHA khi thực sự có widget CAPTCHA
- Sử dụng BeautifulSoup để tìm:
  - CAPTCHA widgets (Geetest, reCAPTCHA, hCaptcha)
  - Script tags load CAPTCHA libraries
  - iframe của CAPTCHA
  - Data attributes của CAPTCHA
- **Không báo sai**: Loại bỏ các từ khóa chung chung
- **Thông báo rõ ràng**: Giải thích lý do và hướng dẫn xử lý

### Input Validation & Security
- **Query sanitization**: Tự động sanitize và validate query input
- **Tax code validation**: Validate mã số thuế (8-15 chữ số)
- **File path validation**: Kiểm tra extension, size, path traversal attacks
- **HTTPS verification**: Explicit SSL certificate verification
- **Error handling**: Specific exceptions cho từng loại lỗi

## ⚠️ Lưu ý

1. **Demo nghiên cứu**: Ứng dụng này chỉ dùng cho mục đích nghiên cứu và học tập

2. **Rate limiting**: Vui lòng không chỉnh sửa rate limit quá thấp để tránh làm quá tải server

3. **HTML parsing**: Nếu masothue.com thay đổi cấu trúc HTML, có thể cần cập nhật parser trong `masothue/client.py`

4. **CAPTCHA**: 
   - Ứng dụng sẽ phát hiện và thông báo khi website yêu cầu CAPTCHA
   - **Không tự động giải CAPTCHA**: Ứng dụng chỉ hỗ trợ phát hiện, không giải tự động
   - Khi gặp CAPTCHA: Mở trình duyệt, giải CAPTCHA thủ công, đợi vài phút rồi thử lại

5. **Cache**: 
   - Cache được lưu trong thư mục `.cache/`
   - Tự động cleanup khi vượt quá 100MB
   - Có thể xóa thư mục `.cache/` để làm mới dữ liệu

## 🐛 Xử lý lỗi

### Lỗi "Không tra cứu được"
- Kiểm tra kết nối internet
- Kiểm tra xem masothue.com có hoạt động không
- Thử lại sau vài phút
- Xem log file trong thư mục `logs/`

### Lỗi "Website yêu cầu xác minh CAPTCHA"
- Mở trình duyệt và truy cập masothue.com
- Giải CAPTCHA thủ công trên website
- Đợi vài phút rồi thử lại trong ứng dụng

### Lỗi "Không đọc được file Excel"
- Kiểm tra file có đúng định dạng .xlsx hoặc .xls không
- Đảm bảo file không đang được mở bởi ứng dụng khác
- Kiểm tra file có quá lớn không (tối đa 50MB)

## 📝 Logging

Ứng dụng tự động log vào file trong thư mục `logs/`:

- **Log file**: `logs/masothue_YYYYMMDD.log`
- **Format**: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`
- **Handlers**: Cả console và file
- **Encoding**: UTF-8

Để bật debug mode, sửa trong `main.py`:

```python
logging.basicConfig(
    level=logging.DEBUG,  # Đổi từ INFO sang DEBUG
    ...
)
```

**Mở file log**: Sử dụng menu "Trợ giúp → 📋 Mở log" trong ứng dụng.

## 🏗️ Kiến trúc

### Thread Safety
- **MasothueClient**: Thread-safe với `threading.Lock()` cho `requests.Session`
- **RateLimiter**: Thread-safe với `threading.Lock()` cho shared state
- **FileCache**: Thread-safe với `threading.Lock()` cho file operations
- **UI Updates**: Thread-safe với `queue.Queue()` cho UI updates từ background threads

### Code Organization
- **Package structure**: Đúng chuẩn Python package với `masothue/` directory
- **Separation of concerns**: Business logic tách khỏi UI
- **Service layer**: `excel_service.py` cho Excel operations, `batch_worker.py` cho batch processing
- **Constants**: Tập trung UI messages vào `masothue/constants.py`
- **Exceptions**: Tập trung custom exceptions vào `masothue/exceptions.py`
- **Theme**: Tập trung colors vào `masothue/theme.py`

## 📄 License

Dự án này chỉ dùng cho mục đích nghiên cứu và học tập.

## 👤 Tác giả

Demo nghiên cứu - Tra cứu mã số thuế

## 🙏 Cảm ơn

- masothue.com - Cung cấp dữ liệu tra cứu
- Các thư viện open source được sử dụng:
  - requests
  - beautifulsoup4
  - openpyxl
  - tkinter (built-in)

## 🔗 Links

- [masothue.com](https://masothue.com) - Website tra cứu mã số thuế

---

**Lưu ý**: Ứng dụng này chỉ dùng cho mục đích nghiên cứu. Vui lòng tuân thủ Terms of Service của masothue.com khi sử dụng.
