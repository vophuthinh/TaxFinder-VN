# views/batch_frame.py
# -*- coding: utf-8 -*-

"""
BatchFrame - View class for batch processing (Excel import/export).
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable


class BatchFrame(ttk.LabelFrame):
    """Frame for batch processing functionality"""
    
    def __init__(self, parent, on_import: Callable[[], None], on_export: Callable[[], None]):
        super().__init__(parent, text="📊 Tra cứu hàng loạt (Excel)", padding=20)
        
        self.on_import_callback = on_import
        self.on_export_callback = on_export
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the batch UI"""
        # Import button
        self.import_button = ttk.Button(
            self,
            text="📥 Nhập Excel",
            command=self.on_import_callback,
            style="Custom.TButton"
        )
        self.import_button.pack(side="left", padx=5)
        
        # Export button
        self.export_button = ttk.Button(
            self,
            text="📤 Xuất Excel",
            command=self.on_export_callback,
            style="Custom.TButton"
        )
        self.export_button.pack(side="left", padx=5)
        
        # Hint
        hint = tk.Label(
            self,
            text="💡 Lưu ý: File Excel cần có cột chứa mã số thuế hoặc tên công ty",
            foreground="#7f8c8d",
            font=("Segoe UI", 9, "italic"),
            background="#ffffff"
        )
        hint.pack(side="left", padx=(25, 0))
    
    def set_buttons_enabled(self, enabled: bool):
        """Enable/disable import and export buttons"""
        state = "normal" if enabled else "disabled"
        self.import_button.config(state=state)
        self.export_button.config(state=state)

