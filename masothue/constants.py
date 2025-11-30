# constants.py
# -*- coding: utf-8 -*-

"""
Constants cho ứng dụng tra cứu mã số thuế
"""

# UI Messages
MSG_SEARCHING = "Đang tra cứu: {query} ({idx}/{total})"
MSG_BATCH_COMPLETE = "✓ Hoàn thành tra cứu {total} công ty."
MSG_BATCH_CANCELLED = "⚡ Đã hủy - Hoàn thành {completed}/{total} công ty"
MSG_BATCH_STOPPED = "⚡ Dừng - Hoàn thành {completed}/{total} công ty"

# Error Messages
ERR_FILE_READ = (
    "Không thể đọc file Excel.\n\n"
    "Nguyên nhân có thể:\n"
    "- File bị khóa bởi ứng dụng khác\n"
    "- Định dạng file không đúng\n"
    "- File bị hỏng\n\n"
    "Chi tiết kỹ thuật: {error}"
)

ERR_FILE_WRITE = (
    "Không thể ghi file Excel.\n\n"
    "Nguyên nhân có thể:\n"
    "- Thư mục không có quyền ghi\n"
    "- File đang được mở bởi ứng dụng khác\n"
    "- Ổ đĩa đầy\n\n"
    "Chi tiết kỹ thuật: {error}"
)

ERR_CAPTCHA = (
    "🔐 Server yêu cầu CAPTCHA\n\n"
    "Đây là hạn chế bảo mật của website để chống bot tự động.\n"
    "Ứng dụng chỉ hỗ trợ phát hiện CAPTCHA, không giải tự động.\n\n"
    "Đã hoàn thành: {completed}/{total} công ty\n\n"
    "💡 Hướng dẫn:\n"
    "1. Mở trình duyệt và truy cập masothue.com\n"
    "2. Giải CAPTCHA thủ công trên website\n"
    "3. Đợi vài phút rồi thử lại trong ứng dụng\n"
    "4. Hoặc tra cứu ít dòng hơn để tránh bị chặn\n\n"
    "⚡ Lưu ý: Đừng tra quá dày để tránh bị chặn.\n\n"
    "Nhấn 'Xuất Excel' để lưu kết quả đã tra cứu."
)

ERR_INVALID_INPUT = "Vui lòng nhập tên công ty hoặc mã số thuế để tra cứu."

ERR_INVALID_FILE_PATH = "Đường dẫn file không hợp lệ."

# Confirmation Messages
CONFIRM_EXIT_BATCH = (
    "Đang tra cứu hàng loạt ({completed}/{total}).\n\n"
    "Bạn có muốn dừng và thoát không?"
)

CONFIRM_CANCEL_BATCH = (
    "Bạn có chắc muốn hủy tra cứu hàng loạt?\n\n"
    "Kết quả đã tra cứu sẽ được giữ lại."
)

CONFIRM_EXPORT = (
    "Tìm thấy {count} công ty để tra cứu.\n"
    "Cột sử dụng: '{column}'\n\n"
    "Quá trình này có thể mất vài phút. Tiếp tục?"
)

CONFIRM_EXIT = "Xác nhận thoát"

# Success Messages
SUCCESS_EXPORT = "Đã xuất kết quả ra file:\n{file_path}"

SUCCESS_BATCH_CANCELLED = (
    "Đã hủy tra cứu hàng loạt.\n"
    "Đã hoàn thành: {completed}/{total} công ty.\n\n"
    "Nhấn 'Xuất Excel' để lưu kết quả đã tra cứu."
)

SUCCESS_BATCH_COMPLETE = (
    "Đã tra cứu xong {total} công ty.\n"
    "Tìm thấy: {found} kết quả.\n\n"
    "Nhấn 'Xuất Excel' để lưu kết quả."
)

# Validation
MAX_QUERY_LENGTH = 200
MIN_QUERY_LENGTH = 1

# File operations
ALLOWED_EXCEL_EXTENSIONS = ['.xlsx', '.xls']
MAX_FILE_SIZE_MB = 50

# UI Messages
MSG_EMPTY_STATE = "Chưa có dữ liệu.\nHãy nhập từ khoá và bấm \"Tra cứu nhanh\" 🚀"
MSG_NO_LOG_FILE = "Chưa có file log nào."
MSG_NO_EXCEL_DATA = "Không tìm thấy dữ liệu để tra cứu trong file Excel."
MSG_NO_SEARCH_RESULTS = "✗ Không tìm thấy kết quả cho: {query}\n\nHãy thử từ khóa khác hoặc kiểm tra lại mã số thuế."
MSG_SEARCH_SUCCESS = "✓ Tìm thấy {count} kết quả (trang 1)."
MSG_SEARCH_ERROR = "✗ Lỗi khi tra cứu"
MSG_NETWORK_ERROR = "✗ Lỗi kết nối"
MSG_NETWORK_ERROR_DETAIL = (
    "Không thể kết nối đến server.\n\n"
    "Chi tiết: {error}\n\n"
    "Vui lòng kiểm tra kết nối internet và thử lại."
)
MSG_VALIDATION_ERROR = "✗ Dữ liệu không hợp lệ"
MSG_CAPTCHA_REQUIRED = "⚡ Website yêu cầu xác minh"
MSG_CAPTCHA_REQUIRED_DETAIL = (
    "🔒 Server yêu cầu CAPTCHA\n\n"
    "Đây là hạn chế bảo mật của website để chống bot tự động.\n"
    "Ứng dụng chỉ hỗ trợ phát hiện CAPTCHA, không giải tự động.\n\n"
    "💡 Hướng dẫn:\n"
    "1. Mở trình duyệt và truy cập masothue.com\n"
    "2. Giải CAPTCHA thủ công trên website\n"
    "3. Đợi vài phút rồi thử lại trong ứng dụng\n"
    "4. Hoặc tra cứu ít dòng hơn để tránh bị chặn\n\n"
    "⚡ Lưu ý: Đừng tra quá dày để tránh bị chặn."
)
MSG_SEARCHING_MST = "✓ Đang tra cứu theo MST"
MSG_NO_DETAIL_INFO = "(Chưa có thông tin)"
MSG_CLEAR_RESULTS = "✓ Đã xóa kết quả"
MSG_CANNOT_OPEN_LOG = "Không thể mở file log:\n{error}"
MSG_INVALID_SETTINGS = "Các giá trị phải là số dương."
MSG_INVALID_NUMBER = "Vui lòng nhập số hợp lệ."
MSG_EXPORT_ERROR = "Không xuất được file Excel.\nChi tiết: {error}"
MSG_SEARCH_ERROR_DETAIL = "Không tra cứu được.\nChi tiết: {error}"
MSG_FILE_INVALID = "File không hợp lệ:\n{error}"
MSG_FILE_READ_ERROR = "Không thể đọc file:\n{error}"
MSG_COLUMN_SELECTION = "Chọn cột để tra cứu"
MSG_COLUMN_SELECTION_INFO = (
    "Không tìm thấy cột phù hợp tự động.\n"
    "Vui lòng chọn cột chứa mã số thuế hoặc tên công ty:"
)
MSG_NO_COLUMNS = "Không có cột"
MSG_NO_COLUMNS_DETAIL = "File Excel không có header. Vui lòng kiểm tra lại file."
MSG_COLUMN_NOT_SELECTED = "Chưa chọn"
MSG_COLUMN_NOT_SELECTED_DETAIL = "Vui lòng chọn một cột."

# Dialog Titles
TITLE_INFO = "Thông tin"
TITLE_ERROR = "Lỗi"
TITLE_WARNING = "Cảnh báo"
TITLE_CONFIRM = "Xác nhận"
TITLE_CONFIRM_CANCEL = "Xác nhận hủy"
TITLE_CAPTCHA = "Website yêu cầu xác minh"
TITLE_NETWORK_ERROR = "Lỗi kết nối"
TITLE_VALIDATION_ERROR = "Lỗi validation"
TITLE_FILE_ERROR = "Lỗi đọc file Excel"
TITLE_EXPORT_ERROR = "Lỗi xuất file Excel"
TITLE_EXIT = "Xác nhận thoát"

