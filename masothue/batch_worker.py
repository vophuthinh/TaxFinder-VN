# batch_worker.py
# -*- coding: utf-8 -*-

"""
Worker class cho batch processing.
Tách biệt logic nghiệp vụ batch processing khỏi UI để tuân thủ Single Responsibility Principle.
"""

import logging
from typing import List, Callable, Optional, Dict, Any

from masothue import MasothueClient, CompanySearchResult
from masothue.exceptions import (
    CaptchaRequiredError,
    NetworkError,
    ParseError,
    CancelledError
)
from masothue.formatters import make_result_row

logger = logging.getLogger(__name__)

# Type aliases
BatchResultDict = Dict[str, str]  # Result dictionary with string keys (may contain spaces)
CompanyDetails = Dict[str, Any]  # Company details from get_company_details


class BatchWorker:
    """
    Worker class xử lý batch processing logic.
    Không phụ thuộc vào UI, chỉ xử lý business logic và gọi callbacks.
    """
    
    def __init__(self, client: MasothueClient):
        """
        Khởi tạo BatchWorker.
        
        Args:
            client: MasothueClient instance để thực hiện tra cứu
        """
        self.client = client
        self._cancelled = False
    
    def process_queries(
        self,
        queries: List[str],
        *,
        cancelled_callback: Optional[Callable[[], bool]] = None,
        progress_callback: Optional[Callable[[int, int, str], None]] = None,
        result_callback: Optional[Callable[[BatchResultDict], None]] = None,
        error_callback: Optional[Callable[[str, Exception], None]] = None,
        captcha_callback: Optional[Callable[[int, int, str], None]] = None
    ) -> List[BatchResultDict]:
        """
        Xử lý batch queries - business logic thuần túy, không có UI logic.
        
        Args:
            queries: Danh sách queries cần tra cứu (MST hoặc tên công ty)
            cancelled_callback: Callback để check xem operation có bị cancel không
            progress_callback: Callback được gọi mỗi khi xử lý xong một query (idx, total, query)
            result_callback: Callback được gọi mỗi khi có kết quả (result_dict)
            error_callback: Callback được gọi khi có lỗi (query, exception)
            captcha_callback: Callback được gọi khi phát hiện CAPTCHA (idx, total, error_msg)
            
        Returns:
            List[BatchResultDict]: Danh sách kết quả tra cứu
            
        Raises:
            CancelledError: Nếu operation bị cancel (chỉ raise nếu không có callback)
            CaptchaRequiredError: Nếu phát hiện CAPTCHA (chỉ raise nếu không có callback)
        """
        self._cancelled = False
        results: List[BatchResultDict] = []
        total = len(queries)
        
        if cancelled_callback:
            self.client.set_cancelled_callback(cancelled_callback)
        
        try:
            for idx, query in enumerate(queries, 1):
                if cancelled_callback and cancelled_callback():
                    self._cancelled = True
                    logger.info(f"Batch processing cancelled at query {idx}/{total}")
                    break
                
                if progress_callback:
                    progress_callback(idx, total, query)
                
                try:
                    result_dict = self._process_single_query(query, cancelled_callback)
                    
                    if result_callback:
                        result_callback(result_dict)
                    
                    results.append(result_dict)
                    
                except CancelledError:
                    self._cancelled = True
                    logger.info(f"Batch processing cancelled during query {idx}/{total}")
                    break
                    
                except CaptchaRequiredError as e:
                    error_msg = str(e)
                    logger.warning(f"CAPTCHA detected at query {idx}/{total}: {error_msg}")
                    
                    if captcha_callback:
                        captcha_callback(idx, total, error_msg)
                    else:
                        raise
                    
                    break
                    
                except (NetworkError, ParseError) as e:
                    logger.error(f"Error processing query '{query}': {str(e)}")
                    error_result = make_result_row(query, error=str(e))
                    
                    if result_callback:
                        result_callback(error_result)
                    
                    results.append(error_result)
                    
                    if error_callback:
                        error_callback(query, e)
                    
                except Exception as e:
                    logger.exception(f"Unexpected error processing query '{query}': {str(e)}")
                    error_result = make_result_row(query, error=str(e))
                    
                    if result_callback:
                        result_callback(error_result)
                    
                    results.append(error_result)
                    
                    if error_callback:
                        error_callback(query, e)
        
        finally:
            self.client.set_cancelled_callback(None)
        
        return results
    
    def _process_single_query(
        self,
        query: str,
        cancelled_callback: Optional[Callable[[], bool]] = None
    ) -> BatchResultDict:
        """
        Xử lý tra cứu một query - chỉ làm business logic, không có UI logic.
        Tối ưu: Check cache trước để skip các query đã có kết quả.
        
        Args:
            query: Query cần tra cứu (MST hoặc tên công ty)
            cancelled_callback: Callback để check cancellation
            
        Returns:
            BatchResultDict: Dict kết quả từ make_result_row()
            
        Raises:
            CancelledError: Nếu operation bị cancel
            CaptchaRequiredError: Nếu website yêu cầu CAPTCHA
            NetworkError: Nếu có lỗi mạng
            ParseError: Nếu có lỗi parse
        """
        if cancelled_callback and cancelled_callback():
            raise CancelledError("Operation đã bị hủy")
        
        # Tra cứu bình thường (search_companies đã nhanh, không cần skip)
        results: List[CompanySearchResult] = self.client.search_companies(query=query, page=1)
        
        if cancelled_callback and cancelled_callback():
            raise CancelledError("Operation đã bị hủy")
        
        if not results:
            return make_result_row(query, result=None)
        
        result = results[0]
        
        # Lấy details (get_company_details tự động check cache và skip nếu có)
        details: Optional[CompanyDetails] = None
        if result.detail_url:
            try:
                details = self.client.get_company_details(result.detail_url)
            except CaptchaRequiredError:
                raise
            except CancelledError:
                raise
            except (NetworkError, ParseError):
                pass
        
        return make_result_row(query, result=result, details=details)
    
    @property
    def is_cancelled(self) -> bool:
        """Kiểm tra xem batch processing có bị cancel không."""
        return self._cancelled

