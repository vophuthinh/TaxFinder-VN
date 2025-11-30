# masothue package
# -*- coding: utf-8 -*-

"""
Masothue - Tra cứu mã số thuế công ty từ masothue.com
"""

__version__ = "1.0.0"

from masothue.models import CompanySearchResult
from masothue.client import MasothueClient
from masothue.exceptions import (
    MasothueError,
    CaptchaRequiredError,
    NetworkError,
    ParseError,
    ValidationError,
    FileError,
    CancelledError
)

__all__ = [
    "CompanySearchResult",
    "MasothueClient",
    "MasothueError",
    "CaptchaRequiredError",
    "NetworkError",
    "ParseError",
    "ValidationError",
    "FileError",
    "CancelledError",
    "__version__"
]

