# rate_limiter.py
# -*- coding: utf-8 -*-

import time
import random
import threading
from collections import deque
from typing import Optional, Dict, Any


class RateLimiter:
    """
    Rate limiter đơn giản để giới hạn số lượng request trong một khoảng thời gian.
    """

    def __init__(
        self,
        max_requests: int = 10,
        time_window: int = 60,
        min_delay: float = 1.0,
        max_delay: float = None,
        use_random_delay: bool = True
    ):
        """
        Args:
            max_requests: Số request tối đa trong time_window
            time_window: Khoảng thời gian tính bằng giây
            min_delay: Thời gian delay tối thiểu giữa các request (giây)
            max_delay: Thời gian delay tối đa (nếu None, dùng min_delay * 3)
            use_random_delay: Nếu True, delay ngẫu nhiên giữa min_delay và max_delay
        """
        self.max_requests = max_requests
        self.time_window = time_window
        self.min_delay = min_delay
        self.max_delay = max_delay or (min_delay * 3)
        self.use_random_delay = use_random_delay
        self.request_times: deque = deque()
        self.last_request_time: Optional[float] = None
        self._lock = threading.Lock()

    def wait_if_needed(self) -> Optional[float]:
        """
        Kiểm tra và chờ nếu cần thiết để tuân thủ rate limit.
        Thread-safe.
        
        Returns:
            Số giây đã chờ (nếu có), None nếu không cần chờ
        """
        with self._lock:
            now = time.time()
            waited = None
            wait_time = 0

            while self.request_times and (now - self.request_times[0]) > self.time_window:
                self.request_times.popleft()

            if len(self.request_times) >= self.max_requests:
                wait_time = self.time_window - (now - self.request_times[0]) + 0.1
                if wait_time <= 0:
                    wait_time = 0
            
            if self.last_request_time is not None:
                time_since_last = now - self.last_request_time
                if self.use_random_delay:
                    target_delay = random.uniform(self.min_delay, self.max_delay)
                else:
                    target_delay = self.min_delay
                
                if time_since_last < target_delay:
                    additional_wait = target_delay - time_since_last
                    wait_time = max(wait_time, additional_wait)

            self.request_times.append(now)
            self.last_request_time = now
        
        if wait_time > 0:
            time.sleep(wait_time)
            waited = wait_time
            now = time.time()
            with self._lock:
                while self.request_times and (now - self.request_times[0]) > self.time_window:
                    self.request_times.popleft()

        return waited
    
    def reset(self) -> None:
        """
        Reset rate limiter về trạng thái ban đầu.
        Xóa tất cả lịch sử request.
        Thread-safe.
        """
        with self._lock:
            self.request_times.clear()
            self.last_request_time = None
    
    def _cleanup(self, now: float) -> None:
        """Xóa các request cũ ngoài time_window"""
        while self.request_times and (now - self.request_times[0]) > self.time_window:
            self.request_times.popleft()
    
    @property
    def current_rate(self) -> int:
        """
        Số request trong time_window hiện tại.
        Thread-safe.
        
        Returns:
            Số request đã thực hiện trong time_window
        """
        with self._lock:
            now = time.time()
            self._cleanup(now)
            return len(self.request_times)
    
    def get_metrics(self) -> Dict[str, Any]:
        """
        Lấy metrics về rate limiter.
        Thread-safe.
        
        Returns:
            Dict với các metrics:
            - current_rate: Số request trong time_window hiện tại
            - max_requests: Số request tối đa cho phép
            - time_window: Khoảng thời gian (giây)
            - requests_per_second: Số request/giây trung bình
            - average_delay: Delay trung bình giữa các request (giây)
        """
        with self._lock:
            now = time.time()
            self._cleanup(now)
            
            current_rate = len(self.request_times)
            
            # Tính requests per second
            if self.request_times:
                oldest_time = self.request_times[0]
                elapsed = now - oldest_time
                requests_per_second = current_rate / elapsed if elapsed > 0 else 0
            else:
                requests_per_second = 0
            
            # Tính average delay
            if self.last_request_time is not None and len(self.request_times) > 1:
                delays = []
                prev_time = self.request_times[0]
                for req_time in list(self.request_times)[1:]:
                    delays.append(req_time - prev_time)
                    prev_time = req_time
                average_delay = sum(delays) / len(delays) if delays else 0
            else:
                average_delay = 0
            
            return {
                'current_rate': current_rate,
                'max_requests': self.max_requests,
                'time_window': self.time_window,
                'requests_per_second': round(requests_per_second, 2),
                'average_delay': round(average_delay, 2),
                'min_delay': self.min_delay,
                'max_delay': self.max_delay,
                'use_random_delay': self.use_random_delay
            }

