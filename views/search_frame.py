# views/search_frame.py
# -*- coding: utf-8 -*-

"""
SearchFrame - View class for quick search functionality.
"""

import tkinter as tk
from tkinter import ttk
from typing import Callable, Optional


class SearchFrame(ttk.LabelFrame):
    """Frame for quick search functionality"""
    
    def __init__(self, parent, on_search: Callable[[str], None], on_query_change: Optional[Callable[[str], None]] = None):
        super().__init__(parent, text="🔍 Tra cứu nhanh", padding=20)
        
        self.on_search_callback = on_search
        self.on_query_change_callback = on_query_change
        
        self._build_ui()
    
    def _build_ui(self):
        """Build the search UI"""
        # Label
        lbl = tk.Label(
            self,
            text="Nhập tên công ty hoặc mã số thuế:",
            font=("Segoe UI", 10),
            bg="#ffffff",
            fg="#2c3e50"
        )
        lbl.pack(side="left", padx=(0, 10))
        
        # Entry
        self.query_var = tk.StringVar()
        self.query_entry = ttk.Entry(
            self,
            textvariable=self.query_var,
            width=55,
            style="Custom.TEntry"
        )
        self.query_entry.pack(side="left", padx=10)
        self.query_entry.bind("<Return>", lambda e: self._on_search_clicked())
        if self.on_query_change_callback:
            self.query_entry.bind("<KeyRelease>", lambda e: self._on_query_changed())
        
        # Status label
        self.status_label = tk.Label(
            self,
            text="",
            font=("Segoe UI", 9, "italic"),
            foreground="#3498db",
            bg="#ffffff"
        )
        self.status_label.pack(side="left", padx=5)
        
        # Search button
        self.search_button = ttk.Button(
            self,
            text="🔎 Tra cứu",
            command=self._on_search_clicked,
            style="Primary.TButton"
        )
        self.search_button.pack(side="left", padx=10)
    
    def _on_search_clicked(self):
        """Handle search button click"""
        query = self.query_var.get().strip()
        if query:
            self.on_search_callback(query)
    
    def _on_query_changed(self):
        """Handle query text change"""
        if self.on_query_change_callback:
            self.on_query_change_callback(self.query_var.get())
    
    def get_query(self) -> str:
        """Get current query text"""
        return self.query_var.get().strip()
    
    def set_query(self, query: str):
        """Set query text"""
        self.query_var.set(query)
    
    def set_status(self, text: str):
        """Set status label text"""
        self.status_label.config(text=text)
    
    def set_search_enabled(self, enabled: bool):
        """Enable/disable search button"""
        state = "normal" if enabled else "disabled"
        self.search_button.config(state=state)
        self.query_entry.config(state=state)

