# exceptions.py
# -*- coding: utf-8 -*-

"""
Custom exceptions cho MasothueClient
"""


class MasothueError(Exception):
    """Base exception cho tất cả lỗi của Masothue"""
    pass


class CaptchaRequiredError(MasothueError):
    """Exception khi website yêu cầu giải CAPTCHA"""
    
    def __init__(self, message: str = None, url: str = None, response_code: int = None):
        """
        Args:
            message: Thông báo lỗi
            url: URL gây ra lỗi
            response_code: HTTP status code
        """
        self.message = message or "Website yêu cầu xác minh CAPTCHA"
        self.url = url
        self.response_code = response_code
        super().__init__(self.message)


class NetworkError(MasothueError):
    """Lỗi liên quan đến network/connection"""
    
    def __init__(self, message: str = None, original_error: Exception = None):
        self.message = message or "Lỗi kết nối mạng"
        self.original_error = original_error
        super().__init__(self.message)


class ParseError(MasothueError):
    """Lỗi khi parse HTML response"""
    
    def __init__(self, message: str = None, html_snippet: str = None):
        self.message = message or "Lỗi khi phân tích HTML"
        self.html_snippet = html_snippet
        super().__init__(self.message)


class ValidationError(MasothueError):
    """Lỗi validation input"""
    
    def __init__(self, message: str = None, field: str = None):
        self.message = message or "Dữ liệu đầu vào không hợp lệ"
        self.field = field
        super().__init__(self.message)


class FileError(MasothueError):
    """Lỗi liên quan đến file operations"""
    
    def __init__(self, message: str = None, file_path: str = None):
        self.message = message or "Lỗi khi thao tác với file"
        self.file_path = file_path
        super().__init__(self.message)


class CancelledError(MasothueError):
    """Exception khi operation bị cancel bởi user"""
    
    def __init__(self, message: str = None):
        self.message = message or "Operation đã bị hủy"
        super().__init__(self.message)

