# config.py
# -*- coding: utf-8 -*-

"""
Cấu hình cho ứng dụng tra cứu mã số thuế
"""

BASE_URL = "https://masothue.com"

DEFAULT_RATE_LIMIT = {
    "max_requests": 10,
    "time_window": 60,
    "min_delay": 1.0,
    "max_delay": 3.0,
    "use_random_delay": True
}

REQUEST_TIMEOUT = 8
REQUEST_RETRIES = 2
REQUEST_RETRY_DELAY = 1

CACHE_ENABLED = True
CACHE_DIR = ".cache"
CACHE_EXPIRY_DAYS = 7
CACHE_MAX_SIZE_MB = 100.0
CACHE_ENABLE_CLEANUP = True

