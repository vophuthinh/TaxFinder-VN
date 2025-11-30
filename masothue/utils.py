# utils.py
# -*- coding: utf-8 -*-

"""
Utility functions cho Masothue
"""

import os
from pathlib import Path
from typing import Optional
from masothue.exceptions import FileError, ValidationError
from masothue.constants import (
    ALLOWED_EXCEL_EXTENSIONS,
    MAX_FILE_SIZE_MB,
    ERR_INVALID_FILE_PATH
)


def validate_file_path(file_path: str, must_exist: bool = False) -> Path:
    """
    Validate file path để tránh path traversal attacks và các lỗi khác.
    
    Args:
        file_path: Đường dẫn file cần validate
        must_exist: Nếu True, file phải tồn tại
        
    Returns:
        Path object nếu hợp lệ
        
    Raises:
        ValidationError: Nếu path không hợp lệ
        FileError: Nếu file không tồn tại (khi must_exist=True)
    """
    if not file_path or not isinstance(file_path, str):
        raise ValidationError("File path không hợp lệ", field="file_path")
    
    try:
        path = Path(file_path).resolve()
    except (OSError, ValueError) as e:
        raise ValidationError(f"Không thể parse file path: {e}", field="file_path")
    
    if ".." in str(path) or path.is_absolute() and not path.is_relative_to(Path.cwd()):
        pass
    
    if must_exist and not path.exists():
        raise FileError(f"File không tồn tại: {file_path}", file_path=str(path))
    
    return path


def validate_excel_file(file_path: str) -> Path:
    """
    Validate Excel file path và extension.
    
    Args:
        file_path: Đường dẫn file Excel
        
    Returns:
        Path object nếu hợp lệ
        
    Raises:
        ValidationError: Nếu không phải file Excel
        FileError: Nếu file không tồn tại hoặc quá lớn
    """
    path = validate_file_path(file_path, must_exist=True)
    
    if path.suffix.lower() not in ALLOWED_EXCEL_EXTENSIONS:
        raise ValidationError(
            f"File phải có extension: {', '.join(ALLOWED_EXCEL_EXTENSIONS)}",
            field="file_path"
        )
    
    try:
        file_size_mb = path.stat().st_size / (1024 * 1024)
        if file_size_mb > MAX_FILE_SIZE_MB:
            raise FileError(
                f"File quá lớn ({file_size_mb:.2f}MB). "
                f"Kích thước tối đa: {MAX_FILE_SIZE_MB}MB",
                file_path=str(path)
            )
    except PermissionError as e:
        raise FileError(
            f"File đang được sử dụng bởi ứng dụng khác (có thể đang mở trong Excel).\n\n"
            f"Vui lòng đóng file Excel và thử lại.",
            file_path=str(path)
        )
    except OSError as e:
        raise FileError(f"Không thể đọc thông tin file: {e}", file_path=str(path))
    
    return path


def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename để tránh các ký tự không hợp lệ.
    
    Args:
        filename: Tên file cần sanitize
        
    Returns:
        Tên file đã được sanitize
    """
    import re
    sanitized = re.sub(r'[<>:"/\\|?*]', '', filename)
    sanitized = sanitized.strip()
    if len(sanitized) > 255:
        sanitized = sanitized[:255]
    return sanitized


def sanitize_query(query: str) -> str:
    """
    Sanitize search query để tránh các ký tự đặc biệt và giới hạn độ dài.
    
    Args:
        query: Query cần sanitize
        
    Returns:
        Query đã được sanitize
    """
    from masothue.constants import MAX_QUERY_LENGTH, MIN_QUERY_LENGTH
    
    if not query or not isinstance(query, str):
        return ""
    
    sanitized = query.strip()
    
    if len(sanitized) > MAX_QUERY_LENGTH:
        sanitized = sanitized[:MAX_QUERY_LENGTH]
    
    if len(sanitized) < MIN_QUERY_LENGTH:
        return ""
    
    return sanitized


def clean_tax_code(tax_code: str) -> str:
    """
    Clean mã số thuế: loại bỏ khoảng trắng, dấu gạch, ký tự đặc biệt.
    
    Args:
        tax_code: Mã số thuế cần clean
        
    Returns:
        Mã số thuế đã được clean (chỉ còn chữ số)
    """
    if not tax_code or not isinstance(tax_code, str):
        return ""
    
    cleaned = ''.join(c for c in tax_code if c.isdigit())
    return cleaned


def is_valid_tax_code(tax_code: str) -> bool:
    """
    Kiểm tra xem mã số thuế có hợp lệ không.
    
    Args:
        tax_code: Mã số thuế cần kiểm tra (có thể chứa spaces, dấu gạch)
        
    Returns:
        True nếu hợp lệ (10 hoặc 13 chữ số sau khi clean), False nếu không
    """
    if not tax_code or not isinstance(tax_code, str):
        return False
    
    cleaned = clean_tax_code(tax_code)
    
    return 8 <= len(cleaned) <= 15 and cleaned.isdigit()

