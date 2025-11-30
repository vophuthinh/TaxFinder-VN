# cache.py
# -*- coding: utf-8 -*-

"""
Cache module cho MasothueClient
Hỗ trợ cả LRU cache (in-memory) và file cache (persistent)
"""

import json
import os
import time
import threading
from functools import lru_cache
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
import hashlib
import logging

logger = logging.getLogger(__name__)


class FileCache:
    """
    File-based cache để lưu kết quả tra cứu vào disk.
    Cache key: tax_code hoặc hash của detail_url
    Hỗ trợ cache size limit và automatic cleanup.
    """
    
    def __init__(
        self, 
        cache_dir: str = ".cache", 
        expiry_days: int = 7,
        max_size_mb: float = 100.0,
        enable_cleanup: bool = True
    ):
        """
        Args:
            cache_dir: Thư mục lưu cache
            expiry_days: Số ngày cache hết hạn
            max_size_mb: Kích thước cache tối đa (MB)
            enable_cleanup: Tự động cleanup cache cũ khi vượt quá size limit
        """
        self.cache_dir = Path(cache_dir)
        self.expiry_days = expiry_days
        self.max_size_mb = max_size_mb
        self.enable_cleanup = enable_cleanup
        self.cache_dir.mkdir(exist_ok=True)
        self._lock = threading.Lock()
    
    def _get_cache_path(self, key: str) -> Path:
        """Lấy đường dẫn file cache cho key"""
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return self.cache_dir / f"{key_hash}.json"
    
    def get(self, key: str) -> Optional[Dict[str, Any]]:
        """
        Lấy giá trị từ cache (thread-safe)
        
        Args:
            key: Cache key (thường là tax_code hoặc detail_url)
        
        Returns:
            Dict nếu tìm thấy và chưa hết hạn, None nếu không
        """
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            if not cache_path.exists():
                return None
            
            try:
                with open(cache_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                cached_time = data.get('_cached_at', 0)
                if time.time() - cached_time > (self.expiry_days * 24 * 3600):
                    try:
                        cache_path.unlink()
                        logger.debug(f"Cache expired for key: {key}")
                    except OSError:
                        pass
                    return None
                
                result = data.copy()
                result.pop('_cached_at', None)
                return result
            except (OSError, json.JSONDecodeError, KeyError) as e:
                logger.warning(f"Error reading cache for key {key}: {e}")
                return None
            except Exception as e:
                logger.exception(f"Unexpected error reading cache for key {key}")
                return None
    
    def set(self, key: str, value: Dict[str, Any]) -> None:
        """
        Lưu giá trị vào cache (thread-safe)
        Tự động cleanup nếu vượt quá size limit.
        
        Args:
            key: Cache key
            value: Dữ liệu cần cache
        """
        cache_path = self._get_cache_path(key)
        
        with self._lock:
            try:
                data = value.copy()
                data['_cached_at'] = time.time()
                
                with open(cache_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                logger.debug(f"Cached data for key: {key}")
                
                if self.enable_cleanup:
                    self._cleanup_if_needed()
            except (OSError, PermissionError) as e:
                logger.warning(f"Error writing cache for key {key}: {e}")
            except Exception as e:
                logger.exception(f"Unexpected error writing cache for key {key}")
                logger.warning(f"Error writing cache for key {key}: {e}")
    
    def _get_cache_size_mb(self) -> float:
        """Tính tổng kích thước cache (MB)"""
        total_size = 0
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                total_size += cache_file.stat().st_size
            except OSError:
                pass
        return total_size / (1024 * 1024)
    
    def _get_cache_files_sorted(self) -> List[Tuple[Path, float, float]]:
        """
        Lấy danh sách cache files sắp xếp theo thời gian (cũ nhất trước).
        
        Returns:
            List of (path, size_mb, cached_time) tuples
        """
        files = []
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                size = cache_file.stat().st_size / (1024 * 1024)
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cached_time = data.get('_cached_at', 0)
                files.append((cache_file, size, cached_time))
            except (OSError, json.JSONDecodeError):
                pass
        
        files.sort(key=lambda x: x[2])
        return files
    
    def _cleanup_if_needed(self) -> None:
        """Cleanup cache nếu vượt quá size limit hoặc hết hạn"""
        current_size = self._get_cache_size_mb()
        
        if current_size <= self.max_size_mb:
            self._cleanup_expired()
            return
        
        logger.info(f"Cache size ({current_size:.2f}MB) exceeds limit ({self.max_size_mb}MB), cleaning up...")
        files = self._get_cache_files_sorted()
        deleted_size = 0
        
        for cache_file, size, cached_time in files:
            if (time.time() - cached_time > (self.expiry_days * 24 * 3600)) or (deleted_size < (current_size - self.max_size_mb)):
                try:
                    cache_file.unlink()
                    deleted_size += size
                    logger.debug(f"Deleted cache file: {cache_file.name}")
                except OSError:
                    pass
            
            if deleted_size >= (current_size - self.max_size_mb):
                break
        
        logger.info(f"Cleaned up {deleted_size:.2f}MB of cache")
    
    def _cleanup_expired(self) -> None:
        """Xóa các cache file đã hết hạn"""
        now = time.time()
        expiry_seconds = self.expiry_days * 24 * 3600
        deleted_count = 0
        
        for cache_file in self.cache_dir.glob("*.json"):
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    cached_time = data.get('_cached_at', 0)
                    if now - cached_time > expiry_seconds:
                        cache_file.unlink()
                        deleted_count += 1
            except (OSError, json.JSONDecodeError):
                pass
        
        if deleted_count > 0:
            logger.debug(f"Cleaned up {deleted_count} expired cache files")
    
    def clear(self) -> None:
        """Xóa tất cả cache (thread-safe)"""
        with self._lock:
            try:
                deleted_count = 0
                for cache_file in self.cache_dir.glob("*.json"):
                    try:
                        cache_file.unlink()
                        deleted_count += 1
                    except OSError:
                        pass
                logger.info(f"Cleared {deleted_count} cache files")
            except (OSError, PermissionError) as e:
                logger.warning(f"Error clearing cache: {e}")
            except Exception as e:
                logger.exception("Unexpected error clearing cache")
                logger.warning(f"Error clearing cache: {e}")
    
    def prune(self) -> Dict[str, Any]:
        """
        Cleanup cache và trả về thống kê.
        
        Returns:
            Dict với thống kê: {'deleted_count': int, 'freed_mb': float, 'current_size_mb': float}
        """
        with self._lock:
            initial_size = self._get_cache_size_mb()
            initial_count = len(list(self.cache_dir.glob("*.json")))
            
            self._cleanup_if_needed()
            
            final_size = self._get_cache_size_mb()
            final_count = len(list(self.cache_dir.glob("*.json")))
            
            return {
                'deleted_count': initial_count - final_count,
                'freed_mb': initial_size - final_size,
                'current_size_mb': final_size,
                'current_count': final_count
            }


def extract_tax_code_from_url(url: str) -> Optional[str]:
    """
    Extract tax code từ detail_url
    
    Args:
        url: URL dạng https://masothue.com/3604062974
    
    Returns:
        Tax code nếu tìm thấy, None nếu không
    """
    import re
    match = re.search(r'/(\d+)/?$', url)
    return match.group(1) if match else None

