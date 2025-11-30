# theme.py
# -*- coding: utf-8 -*-

"""
Theme colors cho ứng dụng tra cứu mã số thuế
Tập trung tất cả màu sắc để dễ dàng thay đổi theme (ví dụ: Dark Mode)
"""


class Theme:
    """
    Theme colors cho UI.
    Tất cả màu sắc được định nghĩa ở đây để dễ dàng thay đổi theme.
    """
    
    # Primary colors
    PRIMARY = "#3498db"  # Xanh dương chính
    PRIMARY_DARK = "#2980b9"  # Xanh dương đậm (hover, active)
    PRIMARY_DARKER = "#1a252f"  # Xanh dương rất đậm (pressed)
    
    # Success colors
    SUCCESS = "#2ecc71"  # Xanh lá
    SUCCESS_DARK = "#27ae60"  # Xanh lá đậm (hover, active)
    
    # Error/Danger colors
    ERROR = "#e74c3c"  # Đỏ
    ERROR_DARK = "#c0392b"  # Đỏ đậm (hover, active)
    
    # Background colors
    BG_MAIN = "#f0f2f5"  # Nền chính (xám nhạt)
    BG_WHITE = "#ffffff"  # Nền trắng
    BG_HEADER = "#2c3e50"  # Nền header (đen nhạt)
    BG_RESULTS_HEADER = "#ecf0f1"  # Nền header kết quả (xám rất nhạt)
    BG_HINT = "#d5e8f7"  # Nền hint (xanh nhạt)
    BG_TREE_EVEN = "#f8f9fa"  # Nền dòng chẵn trong tree
    BG_TREE_ODD = "#ffffff"  # Nền dòng lẻ trong tree
    
    # Text colors
    TEXT_PRIMARY = "#2c3e50"  # Text chính (đen nhạt)
    TEXT_SECONDARY = "#7f8c8d"  # Text phụ (xám)
    TEXT_LIGHT = "#95a5a6"  # Text nhạt (xám nhạt)
    TEXT_WHITE = "#ffffff"  # Text trắng
    TEXT_HEADER = "#ecf0f1"  # Text header (trắng nhạt)
    TEXT_HEADER_SUBTITLE = "#bdc3c7"  # Text subtitle header (xám rất nhạt)
    TEXT_HINT = "#2980b9"  # Text hint (xanh dương)
    
    # Border colors
    BORDER_LIGHT = "#e8e8e8"  # Viền nhạt
    BORDER_MEDIUM = "#bdc3c7"  # Viền trung bình
    BORDER_FOCUS = "#3498db"  # Viền khi focus
    BORDER_TREE = "#bdc3c7"  # Viền tree
    BORDER_ETL = "#3498db"  # Viền ETL loading card
    
    # Button colors
    BTN_SECONDARY = "#bdc3c7"  # Nút secondary (xám)
    BTN_SECONDARY_DARK = "#95a5a6"  # Nút secondary đậm (hover)
    
    # Selected/Hover colors
    SELECTED = "#3498db"  # Màu khi selected
    SELECTED_TEXT = "#ffffff"  # Text khi selected
    
    # Status colors
    STATUS_INFO = "#3498db"  # Status info (xanh)
    STATUS_SUCCESS = "#27ae60"  # Status success (xanh lá)
    STATUS_ERROR = "#e74c3c"  # Status error (đỏ)
    
    @classmethod
    def get_colors(cls) -> dict:
        """
        Trả về dict chứa tất cả màu sắc (để dễ dàng serialize/deserialize).
        
        Returns:
            Dict với tất cả màu sắc
        """
        return {
            "primary": cls.PRIMARY,
            "primary_dark": cls.PRIMARY_DARK,
            "primary_darker": cls.PRIMARY_DARKER,
            "success": cls.SUCCESS,
            "success_dark": cls.SUCCESS_DARK,
            "error": cls.ERROR,
            "error_dark": cls.ERROR_DARK,
            "bg_main": cls.BG_MAIN,
            "bg_white": cls.BG_WHITE,
            "bg_header": cls.BG_HEADER,
            "bg_results_header": cls.BG_RESULTS_HEADER,
            "bg_hint": cls.BG_HINT,
            "bg_tree_even": cls.BG_TREE_EVEN,
            "bg_tree_odd": cls.BG_TREE_ODD,
            "text_primary": cls.TEXT_PRIMARY,
            "text_secondary": cls.TEXT_SECONDARY,
            "text_light": cls.TEXT_LIGHT,
            "text_white": cls.TEXT_WHITE,
            "text_header": cls.TEXT_HEADER,
            "text_header_subtitle": cls.TEXT_HEADER_SUBTITLE,
            "text_hint": cls.TEXT_HINT,
            "border_light": cls.BORDER_LIGHT,
            "border_medium": cls.BORDER_MEDIUM,
            "border_focus": cls.BORDER_FOCUS,
            "border_tree": cls.BORDER_TREE,
            "border_etl": cls.BORDER_ETL,
            "btn_secondary": cls.BTN_SECONDARY,
            "btn_secondary_dark": cls.BTN_SECONDARY_DARK,
            "selected": cls.SELECTED,
            "selected_text": cls.SELECTED_TEXT,
            "status_info": cls.STATUS_INFO,
            "status_success": cls.STATUS_SUCCESS,
            "status_error": cls.STATUS_ERROR,
        }

