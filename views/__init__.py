# views/__init__.py
# -*- coding: utf-8 -*-

"""
View classes for MasothueApp UI components.
Each view is a self-contained tk.Frame that handles its own UI and exposes callbacks.
"""

from views.search_frame import SearchFrame
from views.batch_frame import BatchFrame
from views.results_frame import ResultsFrame
from views.detail_frame import DetailFrame
from views.progress_frame import ProgressFrame

__all__ = [
    "SearchFrame",
    "BatchFrame",
    "ResultsFrame",
    "DetailFrame",
    "ProgressFrame",
]

