# Masothue - Tra cứu Mã số thuế v1.0.0

Ứng dụng desktop Python để tra cứu thông tin doanh nghiệp theo mã số thuế hoặc tên công ty từ website masothue.com.

![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)
![License](https://img.shields.io/badge/License-Research%20Only-yellow.svg)
![Version](https://img.shields.io/badge/Version-1.0.0-green.svg)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg)

## 📋 Mục lục

- [Tính năng](#-tính-năng)
- [Cài đặt](#-cài-đặt)
- [Hướng dẫn sử dụng](#-hướng-dẫn-sử dụng)
- [Cấu trúc dự án](#-cấu-trúc-dự-án)
- [Dependencies](#-dependencies)
- [Troubleshooting](#-troubleshooting)
- [Changelog](#-changelog)
- [Roadmap](#-roadmap)
- [License](#-license)

## ✨ Tính năng

### 🔍 Tra cứu
- **Tra cứu đơn lẻ**: Tìm kiếm công ty theo tên hoặc mã số thuế
- **Tra cứu hàng loạt**: Nhập file Excel và tra cứu nhiều công ty cùng lúc
- **Kết quả chi tiết**: Hiển thị đầy đủ thông tin doanh nghiệp với UI trực quan

### 💾 Dữ liệu
- **Import Excel**: Đọc danh sách công ty từ file Excel (.xlsx, .xls) với auto-detection cột
- **Export Excel**: Xuất kết quả tra cứu ra file Excel với metadata
- **Cache thông minh**: Tự động cache kết quả để tăng tốc độ và giảm request

### ⚙️ Bảo vệ & Tối ưu
- **Rate limiting**: Tự động giới hạn số lượng request để tránh bị chặn
- **Smart Cool-down**: Tự động ngừng và chờ khi phát hiện bị chặn (403/429)
- **User-Agent rotation**: Tự động đổi User-Agent để tránh detection
- **TLS Fingerprinting bypass**: Hỗ trợ `curl_cffi` để giả lập trình duyệt thật
- **Cài đặt nâng cao**: Tùy chỉnh rate limit, cache settings

### 🎨 Giao diện
- **GUI hiện đại**: Giao diện đồ họa với Tkinter, dễ sử dụng
- **CLI**: Command-line interface cho automation
- **Progress tracking**: Theo dõi tiến độ tra cứu hàng loạt
- **Error handling**: Xử lý lỗi thân thiện với người dùng

## 📊 Thông tin lấy được

- ✅ Mã số thuế
- ✅ Tên công ty
- ✅ Địa chỉ Thuế
- ✅ Địa chỉ
- ✅ Người đại diện
- ✅ Điện thoại
- ✅ Tình trạng (Đang hoạt động/Ngừng hoạt động)
- ✅ Ngày hoạt động
- ✅ Quản lý bởi
- ✅ Loại hình DN
- ✅ Ngành nghề chính
- ✅ Ngành nghề khác

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

3. **Cài đặt optional (khuyến nghị)**
```bash
# Cài curl_cffi để vượt qua TLS fingerprinting tốt hơn
pip install curl_cffi
```

4. **Chạy ứng dụng**

**GUI (Giao diện đồ họa):**
```bash
python main.py
```

**CLI (Command Line):**
```bash
# Tra cứu đơn lẻ
python -m masothue.cli search "CÔNG TY TNHH ABC"

# Tra cứu hàng loạt từ Excel
python -m masothue.cli batch input.xlsx output.xlsx
```

## 📖 Hướng dẫn sử dụng

### Tra cứu đơn lẻ

1. Mở ứng dụng: `python main.py`
2. Nhập mã số thuế hoặc tên công ty vào ô tìm kiếm
3. Nhấn nút "⚡ Tra cứu" hoặc nhấn Enter
4. Xem kết quả trong bảng và panel chi tiết bên phải
5. Double-click vào dòng để mở trang web chi tiết

### Tra cứu hàng loạt

1. Chuẩn bị file Excel với cột chứa mã số thuế hoặc tên công ty
2. Nhấn nút "📂 Nhập Excel"
3. Chọn file Excel của bạn
4. Ứng dụng sẽ tự động nhận diện cột chứa dữ liệu (hoặc cho phép bạn chọn thủ công)
5. Xác nhận số lượng công ty cần tra cứu
6. Đợi quá trình tra cứu hoàn thành (có thể hủy bất cứ lúc nào)
7. Nhấn "💾 Xuất Excel" để lưu kết quả

### Cài đặt nâng cao

1. Vào menu "Cài đặt → Cài đặt nâng cao..."
2. Tùy chỉnh:
   - **Rate limiting**: 
     - Số request tối đa (mặc định: 10)
     - Cửa sổ thời gian (mặc định: 60 giây)
     - Độ trễ tối thiểu (mặc định: 1.0 giây)
   - **Cache**: 
     - Bật/tắt cache
     - Thời gian hết hạn (mặc định: 7 ngày)
3. Nhấn "Áp dụng" để lưu

## 🛠️ Cấu trúc dự án

```
Masothue/
├── main.py                 # Entry point cho GUI
├── masothue_cli.py         # Entry point cho CLI (legacy)
├── masothue_app.py         # GUI application (Tkinter)
├── requirements.txt        # Dependencies
├── README.md              # Tài liệu này
│
├── masothue/               # Core package
│   ├── __init__.py        # Package exports
│   ├── client.py           # HTTP client và parsing (với curl_cffi support)
│   ├── cache.py            # Cache management (file-based)
│   ├── batch_worker.py     # Batch processing logic
│   ├── excel_service.py    # Excel I/O operations
│   ├── rate_limiter.py    # Rate limiting với thread safety
│   ├── models.py           # Data models
│   ├── exceptions.py       # Custom exceptions
│   ├── formatters.py       # Data formatting utilities
│   ├── utils.py            # Validation và sanitization
│   ├── config.py           # Configuration constants
│   ├── constants.py        # UI constants
│   ├── theme.py            # UI theme colors
│   └── cli.py              # CLI interface
│
└── views/                  # UI components (future)
    ├── search_frame.py
    └── batch_frame.py
```

## 📦 Dependencies

### Core
- `requests` - HTTP client (fallback nếu không có curl_cffi)
- `beautifulsoup4` - HTML parsing
- `openpyxl` - Excel file handling
- `python-dotenv` - Environment variables

### Optional (khuyến nghị)
- `curl_cffi` - Advanced TLS fingerprinting bypass, giả lập trình duyệt thật

## ⚠️ Lưu ý quan trọng

- ⚠️ **CAPTCHA**: Ứng dụng chỉ hỗ trợ phát hiện CAPTCHA, không giải tự động
- ⚠️ **Rate limiting**: Không tra cứu quá dày để tránh bị chặn IP
- ⚠️ **Terms of Service**: Vui lòng tuân thủ Terms of Service của masothue.com
- ⚠️ **Mục đích**: Dự án này chỉ dùng cho mục đích nghiên cứu và học tập

## 🐛 Troubleshooting

### Lỗi CAPTCHA
Nếu gặp thông báo "Server yêu cầu CAPTCHA":
1. Mở trình duyệt và truy cập masothue.com
2. Giải CAPTCHA thủ công trên website
3. Đợi vài phút rồi thử lại trong ứng dụng
4. Hoặc giảm số lượng request trong batch

### Lỗi kết nối
- Kiểm tra kết nối internet
- Thử lại sau vài phút
- Kiểm tra file log trong thư mục `logs/`
- Cài đặt `curl_cffi` để cải thiện khả năng kết nối:
  ```bash
  pip install curl_cffi
  ```

### Lỗi 403/429 (Bị chặn)
- Ứng dụng tự động phát hiện và kích hoạt "Smart Cool-down"
- Đợi 60 giây (hoặc theo Retry-After header) rồi tự động retry
- Nếu vẫn bị chặn, đợi lâu hơn hoặc giảm rate limit

### Lỗi đọc Excel
- Đảm bảo file Excel không bị khóa bởi ứng dụng khác
- Kiểm tra định dạng file (.xlsx hoặc .xls)
- Đảm bảo file không bị hỏng

## 📝 Logging

Ứng dụng tự động ghi log vào thư mục `logs/`:
- File log: `logs/masothue_YYYYMMDD.log`
- Mở log: Menu "Trợ giúp → Mở log"
- Log level: DEBUG, INFO, WARNING, ERROR

## 📋 Changelog

### v1.0.0 (2024-12-01)

**Tính năng chính:**
- ✅ Tra cứu đơn lẻ và hàng loạt
- ✅ Import/Export Excel với auto-detection cột
- ✅ Cache thông minh (file-based)
- ✅ Rate limiting với thread safety
- ✅ Smart Cool-down khi bị chặn (403/429)
- ✅ User-Agent rotation
- ✅ Hỗ trợ curl_cffi (TLS fingerprinting bypass)
- ✅ GUI và CLI interface
- ✅ Progress tracking và cancellation
- ✅ Error handling toàn diện

**Cải tiến:**
- Tối ưu HTML parsing (tránh double parsing)
- Thread-safe operations
- Input validation và sanitization
- UI responsive với mouse wheel scrolling

## 🗺️ Roadmap

### v1.1.0 (Planned)
- [ ] Export nhiều định dạng (CSV, JSON)
- [ ] Filter và sort nâng cao trong GUI
- [ ] Dark mode
- [ ] Multi-language support

### v1.2.0 (Future)
- [ ] Database integration (SQLite)
- [ ] Scheduled batch processing
- [ ] API server mode
- [ ] Webhook notifications

### v2.0.0 (Future)
- [ ] Multi-threaded batch processing
- [ ] Proxy support
- [ ] Advanced analytics dashboard
- [ ] Plugin system

## 📄 License

Dự án này chỉ dùng cho mục đích nghiên cứu và học tập.

**Lưu ý**: Vui lòng tuân thủ Terms of Service của masothue.com khi sử dụng ứng dụng này.

## 👤 Tác giả

Dự án mã nguồn mở cho cộng đồng.

## 🤝 Đóng góp

Mọi đóng góp đều được chào đón! 

1. Fork dự án
2. Tạo feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Mở Pull Request

### Guidelines
- Tuân thủ PEP 8 style guide
- Viết docstrings cho functions/classes
- Thêm tests nếu có thể
- Update README nếu cần

## 📞 Hỗ trợ

- Tạo issue trên GitHub để báo lỗi hoặc đề xuất tính năng
- Xem file log trong thư mục `logs/` để debug
- Đọc documentation trong code comments

---

**Made with ❤️ for the community**

*Version 1.0.0 - December 2024*
