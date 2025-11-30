# masothue_client.py
# -*- coding: utf-8 -*-

import logging
import time
import threading
import random

from typing import List, Optional, Callable, Dict, Any
from urllib.parse import urljoin

try:
    from curl_cffi import requests as cffi_requests
    CURL_CFFI_AVAILABLE = True
    # curl_cffi có thể raise exceptions từ module riêng của nó
    try:
        from curl_cffi.requests import HTTPError as CffiHTTPError, RequestException as CffiRequestException
    except (ImportError, AttributeError):
        # Fallback: curl_cffi có thể dùng chung exceptions với requests
        CffiHTTPError = None
        CffiRequestException = None
except ImportError:
    cffi_requests = None
    CURL_CFFI_AVAILABLE = False
    CffiHTTPError = None
    CffiRequestException = None

# Import requests và exceptions
import requests
HTTPError = requests.HTTPError
RequestException = requests.RequestException

# Tạo tuple exceptions để catch cả hai loại
if CffiHTTPError and CffiRequestException:
    HTTPErrorTypes = (HTTPError, CffiHTTPError)
    RequestExceptionTypes = (RequestException, CffiRequestException)
else:
    HTTPErrorTypes = (HTTPError,)
    RequestExceptionTypes = (RequestException,)

from bs4 import BeautifulSoup

from masothue.rate_limiter import RateLimiter
from masothue.config import BASE_URL, DEFAULT_RATE_LIMIT, REQUEST_TIMEOUT, REQUEST_RETRIES, REQUEST_RETRY_DELAY

logger = logging.getLogger(__name__)


from masothue.models import CompanySearchResult
from masothue.cache import FileCache, extract_tax_code_from_url
from masothue.config import (
    CACHE_ENABLED, 
    CACHE_DIR, 
    CACHE_EXPIRY_DAYS,
    CACHE_MAX_SIZE_MB,
    CACHE_ENABLE_CLEANUP
)
from masothue.exceptions import (
    CaptchaRequiredError,
    NetworkError,
    ParseError,
    ValidationError,
    CancelledError
)
from masothue.utils import sanitize_query

import re
CAPTCHA_WIDGET_PATTERNS = [
    re.compile(r'geetest', re.I),
    re.compile(r'g-recaptcha', re.I),
    re.compile(r'h-captcha', re.I),
    re.compile(r'captcha-container', re.I),
    re.compile(r'captcha-box', re.I),
    re.compile(r'captcha-wrapper', re.I),
    re.compile(r'captcha-widget', re.I),
    re.compile(r'gt_holder', re.I),
    re.compile(r'gt_box', re.I),
]

CAPTCHA_TEXT_PATTERN = re.compile(r'geetest|recaptcha|hcaptcha', re.I)

# Danh sách User-Agent hiện đại
USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Edge/122.0.0.0"
]


class MasothueClient:
    """
    Client đơn giản để tra cứu MST công ty trên masothue.com
    """

    def __init__(
        self,
        max_requests: int = None,
        time_window: int = None,
        min_delay: float = None,
        timeout: int = None,
        enable_cache: bool = None,
        cache_dir: str = None,
        cache_expiry_days: int = None
    ):
        # Sử dụng curl_cffi nếu có, fallback về requests
        if CURL_CFFI_AVAILABLE:
            # Giả lập Chrome 120 để vượt qua TLS fingerprinting
            self.session = cffi_requests.Session(impersonate="chrome120")
            logger.info("Using curl_cffi with Chrome 120 impersonation")
        else:
            import requests
            self.session = requests.Session()
            logger.info("Using standard requests library (curl_cffi not available, install with: pip install curl_cffi)")
        
        self.session.headers.update({
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "vi-VN,vi;q=0.9,en;q=0.8",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive"
        })
        # Random User-Agent ngay khi khởi tạo (chỉ nếu dùng requests, curl_cffi tự động set)
        if not CURL_CFFI_AVAILABLE:
            self._rotate_user_agent()
        self.timeout = timeout or REQUEST_TIMEOUT
        self._lock = threading.Lock()
        self._cancelled_callback: Optional[callable] = None
        self.rate_limiter = RateLimiter(
            max_requests=max_requests or DEFAULT_RATE_LIMIT["max_requests"],
            time_window=time_window or DEFAULT_RATE_LIMIT["time_window"],
            min_delay=min_delay or DEFAULT_RATE_LIMIT["min_delay"],
            max_delay=DEFAULT_RATE_LIMIT.get("max_delay", 3.0),
            use_random_delay=DEFAULT_RATE_LIMIT.get("use_random_delay", True)
        )
        self.cache_enabled = enable_cache if enable_cache is not None else CACHE_ENABLED
        if self.cache_enabled:
            self.file_cache = FileCache(
                cache_dir=cache_dir or CACHE_DIR,
                expiry_days=cache_expiry_days or CACHE_EXPIRY_DAYS,
                max_size_mb=CACHE_MAX_SIZE_MB,
                enable_cleanup=CACHE_ENABLE_CLEANUP
            )
        else:
            self.file_cache = None
    
    def _rotate_user_agent(self):
        """Đổi User-Agent ngẫu nhiên"""
        ua = random.choice(USER_AGENTS)
        self.session.headers.update({"User-Agent": ua})
        logger.debug(f"Rotated User-Agent to: {ua}")

    def set_cancelled_callback(self, callback: Optional[Callable[[], bool]]) -> None:
        """
        Set callback để check nếu operation bị cancel.
        Callback được gọi giữa các retry để cho phép cancel nhanh hơn.
        
        Args:
            callback: Function không tham số, trả về True nếu cancelled, False nếu không
        """
        self._cancelled_callback = callback

    def _get_html_and_soup(self, path: str, params: dict, retries: int = None) -> tuple[str, BeautifulSoup]:
        """
        Internal method: Gửi request GET và trả về cả HTML và BeautifulSoup.
        Tối ưu để tránh double parsing - parse một lần và reuse soup.
        
        Args:
            path: Đường dẫn API hoặc full URL
            params: Query parameters (nếu path là full URL thì params sẽ bị bỏ qua)
            retries: Số lần retry (mặc định từ config)
        
        Returns:
            Tuple (html_content, soup) - HTML string và BeautifulSoup object
        
        Raises:
            CancelledError: Nếu operation bị cancel
            requests.RequestException: Nếu tất cả retry đều thất bại
        """
        if path.startswith(('http://', 'https://')):
            url = path
        else:
            url = urljoin(BASE_URL, path)
        
        retries = retries or REQUEST_RETRIES
        current_timeout = self.timeout

        for attempt in range(retries):
            if self._cancelled_callback and self._cancelled_callback():
                logger.debug("Request cancelled, raising CancelledError")
                raise CancelledError("Operation đã bị hủy bởi người dùng")
            
            waited = self.rate_limiter.wait_if_needed()
            if waited:
                logger.debug("Waited %.2fs before request", waited)
            
            if self._cancelled_callback and self._cancelled_callback():
                logger.debug("Request cancelled after wait, raising CancelledError")
                raise CancelledError("Operation đã bị hủy bởi người dùng")

            try:
                with self._lock:
                    resp = self.session.get(url, params=params, timeout=current_timeout, verify=True)
                    resp.raise_for_status()
                    
                    html_content = resp.text
                    
                    soup = BeautifulSoup(html_content, "html.parser")
                    
                    if self._has_captcha(html_content, soup=soup):
                        raise CaptchaRequiredError(
                            message="Website yêu cầu xác minh CAPTCHA. "
                                    "Vui lòng mở trình duyệt, giải CAPTCHA rồi thử lại sau.",
                            url=url,
                            response_code=resp.status_code
                        )
                    
                    return (html_content, soup)
                    
            except HTTPErrorTypes as e:
                status_code = e.response.status_code
                logger.warning(
                    f"HTTP error {status_code} khi request {url}: {e}",
                    extra={"url": url, "status_code": status_code}
                )
                
                # Nếu bị chặn (403) hoặc quá tải (429) - Smart Cool-down
                if status_code in [403, 429]:
                    logger.error(f"⚠️ Phát hiện bị chặn (HTTP {status_code}). Kích hoạt Cool-down.")
                    
                    # Xóa cookie để reset session
                    self.session.cookies.clear()
                    self._rotate_user_agent()  # Đổi nhận diện
                    
                    # Ngủ dài hơn nhiều so với retry bình thường
                    # 429 thường có header Retry-After, nếu không có thì ngủ 30-60s
                    try:
                        retry_after = e.response.headers.get("Retry-After", "30")
                        wait_time = int(retry_after)
                    except (ValueError, TypeError):
                        wait_time = 30  # Default nếu không parse được
                    
                    # Nếu là 403 (Forbidden), ngủ lâu hơn để server thả IP
                    if status_code == 403:
                        wait_time = max(wait_time, 60)
                    
                    logger.info(f"Đang 'ngủ đông' {wait_time} giây để tránh bị ban vĩnh viễn...")
                    
                    # Check cancellation trong khi chờ
                    if self._cancelled_callback:
                        # Chia wait_time thành các chunk nhỏ để check cancellation
                        chunk_size = 5  # Check mỗi 5 giây
                        remaining = wait_time
                        while remaining > 0:
                            if self._cancelled_callback():
                                logger.debug("Request cancelled during cool-down, raising CancelledError")
                                raise CancelledError("Operation đã bị hủy bởi người dùng")
                            sleep_time = min(chunk_size, remaining)
                            time.sleep(sleep_time)
                            remaining -= sleep_time
                    else:
                        time.sleep(wait_time)
                    
                    # Sau khi ngủ dậy, retry lại request này (nếu còn lượt)
                    if attempt < retries - 1:
                        continue
                    else:
                        # Hết lượt thì raise lỗi ra ngoài
                        raise NetworkError(
                            message=f"Lỗi HTTP {status_code} khi truy cập {url} (đã thử cool-down)",
                            url=url,
                            status_code=status_code,
                            original_error=e
                        )
                
                # Xử lý các lỗi HTTP khác (không phải 403/429)
                if attempt == retries - 1:
                    raise NetworkError(
                        message=f"Lỗi HTTP {status_code} khi truy cập {url}",
                        url=url,
                        status_code=status_code,
                        original_error=e
                    )
                
                if self._cancelled_callback and self._cancelled_callback():
                    logger.debug("Request cancelled after request error, raising CancelledError")
                    raise CancelledError("Operation đã bị hủy bởi người dùng")
                
                delay = REQUEST_RETRY_DELAY * (attempt + 1)
                logger.debug("Chờ %s giây trước khi retry...", delay)
                time.sleep(delay)
                
            except RequestExceptionTypes as e:
                logger.warning(f"Request error khi request {url} (attempt {attempt + 1}/{retries}): {e}")
                
                if attempt == retries - 1:
                    raise NetworkError(
                        message=f"Lỗi kết nối khi truy cập {url}: {str(e)}",
                        url=url,
                        original_error=e
                    )
                
                if self._cancelled_callback and self._cancelled_callback():
                    logger.debug("Request cancelled after request error, raising CancelledError")
                    raise CancelledError("Operation đã bị hủy bởi người dùng")
                
                delay = REQUEST_RETRY_DELAY * (attempt + 1)
                logger.debug("Chờ %s giây trước khi retry...", delay)
                time.sleep(delay)
        
        raise NetworkError(message="Unexpected error in _get_html_and_soup", url=url)
    
    def _get(self, path: str, params: dict, retries: int = None) -> str:
        """
        Gửi request GET tới masothue với rate limit và retry logic.
        Hỗ trợ cancellation: check callback giữa các retry.
        
        Args:
            path: Đường dẫn API hoặc full URL
            params: Query parameters (nếu path là full URL thì params sẽ bị bỏ qua)
            retries: Số lần retry (mặc định từ config)
        
        Returns:
            HTML content
        
        Raises:
            CancelledError: Nếu operation bị cancel
            requests.RequestException: Nếu tất cả retry đều thất bại
        """
        html, _ = self._get_html_and_soup(path, params, retries)
        return html
    
    def _has_captcha(self, html_content: str, soup: BeautifulSoup = None) -> bool:
        """
        Kiểm tra xem HTML response có chứa CAPTCHA không.
        Tối ưu: Check string patterns trước (nhanh), chỉ tạo soup khi thực sự cần thiết
        để tránh double parsing (parse trong _get() và parse lại trong search_companies/get_company_details).
        
        Args:
            html_content: Nội dung HTML từ response
            soup: BeautifulSoup object (optional, sẽ tạo mới nếu không có)
            
        Returns:
            True nếu phát hiện CAPTCHA thực sự, False nếu không
        """
        try:
            html_lower = html_content.lower()
            
            quick_indicators = [
                'geetest',
                'recaptcha',
                'hcaptcha',
                'captcha.js',
                'gt.js',
                'data-sitekey',
                'data-widget-id',
                'vui lòng xác minh bạn không phải robot',
                'please verify you are not a robot',
            ]
            
            if not any(indicator in html_lower for indicator in quick_indicators):
                return False
            
            if soup is None:
                soup = BeautifulSoup(html_content, 'html.parser')
            
            for selector_pattern in CAPTCHA_WIDGET_PATTERNS:
                if soup.find(class_=selector_pattern) or soup.find(id=selector_pattern):
                    logger.debug(f"Phát hiện CAPTCHA widget: {selector_pattern.pattern}")
                    return True
            
            for script in soup.find_all('script', src=True):
                src = script.get('src', '').lower()
                if any(indicator in src for indicator in ['geetest', 'recaptcha', 'hcaptcha', 'captcha.js', 'gt.js']):
                    logger.debug(f"Phát hiện CAPTCHA script: {src}")
                    return True
            
            for iframe in soup.find_all('iframe'):
                src = iframe.get('src', '').lower()
                if any(indicator in src for indicator in ['recaptcha', 'hcaptcha', 'geetest']):
                    logger.debug(f"Phát hiện CAPTCHA iframe: {src}")
                    return True
            
            captcha_data_attrs = ['data-sitekey', 'data-callback', 'data-widget-id']
            for attr in captcha_data_attrs:
                if soup.find(attrs={attr: True}):
                    logger.debug(f"Phát hiện CAPTCHA qua data attribute: {attr}")
                    return True
            
            specific_captcha_texts = [
                'vui lòng xác minh bạn không phải robot',
                'please verify you are not a robot',
                'vui lòng hoàn thành xác minh',
                'please complete the verification',
            ]
            for text in specific_captcha_texts:
                if text in html_lower:
                    widget = soup.find(class_=CAPTCHA_TEXT_PATTERN)
                    if widget:
                        logger.debug(f"Phát hiện CAPTCHA qua text: {text}")
                        return True
            
            return False
        except (AttributeError, ValueError, TypeError) as e:
            logger.warning(f"Error parsing HTML with BeautifulSoup, falling back to string search: {e}")
        except Exception as e:
            logger.exception("Unexpected error in _has_captcha")
            html_lower = html_content.lower()
            return any(keyword in html_lower for keyword in ['geetest', 'g-recaptcha', 'h-captcha'])


    def search_companies(
        self, 
        query: str, 
        page: int = 1, 
        fetch_details: bool = False
    ) -> List[CompanySearchResult]:
        """
        Tìm kiếm công ty theo tên hoặc MST.
        Hiện tại dùng chế độ 'auto' của masothue.
        
        Args:
            query: Tên công ty hoặc mã số thuế
            page: Số trang (mặc định 1)
            fetch_details: Nếu True, fetch chi tiết đầy đủ cho tất cả kết quả có detail_url
        
        Returns:
            Danh sách kết quả tìm kiếm
            
        Raises:
            ValidationError: Nếu query không hợp lệ
            NetworkError: Nếu có lỗi network
            CaptchaRequiredError: Nếu website yêu cầu CAPTCHA
        """
        query = sanitize_query(query)
        if not query:
            raise ValidationError("Query trống", field="query")

        params = {
            "q": query.strip(),
            "type": "auto",
        }
        if page > 1:
            params["page"] = page

        html, soup = self._get_html_and_soup("/Search/", params=params)
        results = self._parse_search_results(html, soup=soup)
        
        query_clean = query.strip()
        is_tax_code = query_clean.isdigit()
        
        if is_tax_code:
            for result in results:
                if result.tax_code == query_clean:
                    if result.detail_url:
                        try:
                            detail_info = self.get_company_details(result.detail_url)
                            self._update_result_from_details(result, detail_info)
                        except (NetworkError, ParseError, CaptchaRequiredError, CancelledError) as e:
                            if isinstance(e, (CancelledError, CaptchaRequiredError)):
                                raise
                            logger.warning(f"Không lấy được chi tiết từ {result.detail_url}: {e}")
                        except Exception as e:
                            logger.exception(f"Unexpected error fetching details from {result.detail_url}")
                            logger.warning(f"Không lấy được chi tiết từ {result.detail_url}: {e}")
                    return [result]
            return []
        
        if fetch_details:
            for result in results:
                if result.detail_url:
                    try:
                        detail_info = self.get_company_details(result.detail_url)
                        self._update_result_from_details(result, detail_info)
                    except Exception as e:
                        logger.warning(f"Không lấy được chi tiết từ {result.detail_url}: {e}")
        
        return results
    
    def _update_result_from_details(
        self, 
        result: CompanySearchResult, 
        detail_info: dict
    ) -> None:
        """Helper method để cập nhật result từ detail_info"""
        result.tax_address = detail_info.get('tax_address')
        result.address = detail_info.get('address') or result.address
        result.representative = detail_info.get('representative') or result.representative
        result.phone = detail_info.get('phone')
        result.status = detail_info.get('status')
        result.operation_date = detail_info.get('operation_date')
        result.managed_by = detail_info.get('managed_by')
        result.business_type = detail_info.get('business_type')
        result.main_business = detail_info.get('main_business')
        result.other_businesses = detail_info.get('other_businesses')


    def _parse_search_results(self, html: str, soup: BeautifulSoup = None) -> List[CompanySearchResult]:
        """
        Parse HTML của trang Search.
        Tối ưu: Nhận soup như optional parameter để tránh double parsing.
        
        Args:
            html: HTML content string
            soup: BeautifulSoup object (optional, sẽ tạo mới nếu không có)
        
        Lưu ý: Selector có thể phải chỉnh nếu masothue đổi giao diện.
        """
        if soup is None:
            soup = BeautifulSoup(html, "html.parser")
        results: List[CompanySearchResult] = []

        for label in soup.find_all(string=lambda s: s and "Mã số thuế:" in s):
            p_mst = label.parent
            if not p_mst:
                continue

            tax_link = p_mst.find("a")
            if tax_link:
                tax_code = tax_link.get_text(strip=True)
            else:
                tax_code = label.split("Mã số thuế:")[-1].strip()

            h3 = p_mst.find_previous("h3")
            if h3:
                a_company = h3.find("a")
                if a_company:
                    name = a_company.get_text(strip=True)
                    detail_url = urljoin(BASE_URL, a_company.get("href"))
                else:
                    name = h3.get_text(strip=True)
                    detail_url = None
            else:
                name = ""
                detail_url = None

            rep_name = None
            rep_label = p_mst.find_next(string=lambda s: s and "Người đại diện" in s)
            if rep_label:
                rep_container = rep_label.parent
                rep_link = rep_container.find("a")
                if rep_link:
                    rep_name = rep_link.get_text(strip=True)
                else:
                    rep_name = rep_label.replace("Người đại diện:", "").strip()

            address = None
            if rep_label:
                rep_container = rep_label.parent
                for sib in rep_container.next_siblings:
                    if getattr(sib, "name", None) is None:
                        continue
                    addr_text = sib.get_text(" ", strip=True)
                    if addr_text:
                        address = addr_text
                        break

            if not name and not tax_code:
                continue

            results.append(CompanySearchResult(
                name=name,
                tax_code=tax_code,
                representative=rep_name,
                address=address,
                detail_url=detail_url
            ))

        return results
    
    def _is_valid_representative_name(self, text: str) -> bool:
        """Kiểm tra xem text có phải là tên người đại diện hợp lệ không"""
        if not text or len(text) < 2 or len(text) > 100:
            return False
        if text.isdigit() and len(text) in [10, 13]:
            return False
        if not any(c.isalpha() for c in text):
            return False
        digit_count = sum(1 for c in text if c.isdigit())
        if digit_count > len(text) * 0.5:
            return False
        invalid_keywords = ["Mã số thuế", "MST", "Tax", "Code", "Địa chỉ", "Address"]
        if any(keyword in text for keyword in invalid_keywords):
            return False
        return True
    
    def _get_value_by_label(self, soup: BeautifulSoup, label_text: str) -> Optional[str]:
            """Tìm giá trị theo label - tìm trong nhiều cách khác nhau"""
            label_elem = soup.find(string=lambda s: s and label_text in s)
            if not label_elem:
                return None
            
            parent = label_elem.parent
            if not parent:
                return None
            
            parent_full_text = parent.get_text(separator=" ", strip=True)
            if ":" in parent_full_text:
                parts = parent_full_text.split(":", 1)
                if len(parts) > 1:
                    value = parts[-1].strip()
                    value = value.replace(label_text, "").strip()
                    if value and len(value) > 0:
                        return value
            
            for tag_name in ['a', 'strong', 'span', 'div', 'p']:
                for tag in parent.find_all(tag_name):
                    tag_text = tag.get_text(strip=True)
                    if tag_text and label_text not in tag_text and len(tag_text) > 1:
                        if ":" not in tag_text or tag_text.split(":")[0].strip() != label_text:
                            return tag_text
            
            for sibling in parent.next_siblings:
                if hasattr(sibling, 'get_text'):
                    sibling_text = sibling.get_text(strip=True)
                    if sibling_text and label_text not in sibling_text:
                        return sibling_text
            
            if parent.parent:
                for child in parent.parent.find_all(['div', 'p', 'span']):
                    child_text = child.get_text(strip=True)
                    if label_text in child_text and ":" in child_text:
                        parts = child_text.split(":", 1)
                        if len(parts) > 1:
                            value = parts[-1].strip()
                            if value and value != label_text:
                                return value
            
            return None
        
    def _parse_other_businesses_table(self, soup: BeautifulSoup) -> List[str]:
        """Parse bảng ngành nghề kinh doanh khác từ HTML"""
        other_businesses_list = []
        for table in soup.find_all('table', class_='table'):
            thead = table.find('thead')
            if thead:
                header_text = thead.get_text(strip=True)
                if 'Mã' in header_text and 'Ngành' in header_text:
                    tbody = table.find('tbody')
                    if tbody:
                        for row in tbody.find_all('tr'):
                            tds = row.find_all('td')
                            if len(tds) >= 2:
                                code_td = tds[0]
                                code_link = code_td.find('a')
                                code = code_link.get_text(strip=True) if code_link else code_td.get_text(strip=True)
                                
                                name_td = tds[1]
                                name_link = name_td.find('a')
                                if name_link:
                                    name = name_link.get_text(strip=True)
                                else:
                                    name = name_td.get_text(strip=True)
                                
                                if code and name:
                                    business_item = f"{code} - {name}"
                                    other_businesses_list.append(business_item)
                                    logger.debug(f"Tìm thấy ngành nghề khác: {business_item}")
        return other_businesses_list
    
    def _parse_representative(self, soup: BeautifulSoup, details: dict) -> None:
        """
        Parse người đại diện từ HTML - sử dụng nhiều cách khác nhau.
        Updates details dict in-place.
        
        Refactored để giảm cyclomatic complexity bằng cách tách thành các helper methods.
        """
        if details.get('representative'):
            logger.debug("[PARSING] Representative: Đã có sẵn, bỏ qua")
            return
        
        rep_name = None
        method_used = None
        
        rep_name, method_used = self._extract_rep_from_container_structure(soup)
        
        if not rep_name:
            rep_elem = soup.find(string=lambda s: s and "Người đại diện" in s)
            if rep_elem:
                rep_parent = rep_elem.parent
                
                rep_name, method_used = self._extract_rep_from_parent_link(rep_parent)
                if not rep_name:
                    rep_name, method_used = self._extract_rep_from_parent_strong_b(rep_parent)
                if not rep_name:
                    rep_name, method_used = self._extract_rep_from_parent_span_div_p(rep_parent)
                if not rep_name:
                    rep_name, method_used = self._extract_rep_from_parent_text(rep_parent)
                if not rep_name:
                    rep_name, method_used = self._extract_rep_from_sibling(rep_parent)
                if not rep_name:
                    rep_name, method_used = self._extract_rep_from_parent_container(rep_parent)
        
        if not rep_name:
            rep_name, method_used = self._extract_rep_from_pattern_matching(soup)
        
        if rep_name:
            cleaned_name = self._clean_representative_name(rep_name)
            if cleaned_name:
                details['representative'] = cleaned_name
                if method_used:
                    logger.debug(f"[PARSING] Representative: Đã lưu với method '{method_used}'")
                logger.info(f"[PARSING] Representative: Kết quả cuối cùng (method: {method_used}): {cleaned_name}")
            else:
                logger.warning(f"Tên người đại diện không hợp lệ sau khi làm sạch: '{rep_name}'")
        else:
            logger.warning("[PARSING] Representative: Không tìm thấy người đại diện sau tất cả các cách")
    
    def _extract_rep_from_container_structure(self, soup: BeautifulSoup) -> tuple[Optional[str], Optional[str]]:
        """Extract representative từ container structure (Cách 0)."""
        for container in soup.find_all(['div', 'section', 'article']):
            container_text = container.get_text(strip=True)
            if "Người đại diện" in container_text:
                for tag in container.find_all(['a', 'strong', 'b', 'span']):
                    tag_text = tag.get_text(strip=True)
                    if (tag_text and
                        "Người đại diện" not in tag_text and
                        ":" not in tag_text and
                        self._is_valid_representative_name(tag_text)):
                        logger.debug(f"[PARSING] Representative: Tìm thấy từ container structure (Cách 0): {tag_text}")
                        return tag_text, "container-structure"
        return None, None
    
    def _extract_rep_from_parent_link(self, rep_parent) -> tuple[Optional[str], Optional[str]]:
        """Extract representative từ link trong parent (Ưu tiên 1)."""
        rep_link = rep_parent.find("a", href=True)
        if rep_link:
            candidate = rep_link.get_text(strip=True)
            if self._is_valid_representative_name(candidate):
                logger.info(f"[PARSING] Representative: Tìm thấy từ <a> trong parent (Cách 1): {candidate}")
                return candidate, "link-in-parent"
        return None, None
    
    def _extract_rep_from_parent_strong_b(self, rep_parent) -> tuple[Optional[str], Optional[str]]:
        """Extract representative từ strong/b trong parent (Ưu tiên 2)."""
        for tag_name in ['strong', 'b']:
            rep_tag = rep_parent.find(tag_name)
            if rep_tag:
                candidate = rep_tag.get_text(strip=True)
                if self._is_valid_representative_name(candidate):
                    logger.info(f"[PARSING] Representative: Tìm thấy từ <{tag_name}> trong parent (Cách 1): {candidate}")
                    return candidate, f"strong-b-in-parent-{tag_name}"
        return None, None
    
    def _extract_rep_from_parent_span_div_p(self, rep_parent) -> tuple[Optional[str], Optional[str]]:
        """Extract representative từ span/div/p trong parent (Ưu tiên 3)."""
        for tag_name in ['span', 'div', 'p']:
            for tag in rep_parent.find_all(tag_name):
                tag_text = tag.get_text(strip=True)
                if (tag_text and 
                    "Người đại diện" not in tag_text and
                    ":" not in tag_text and
                    self._is_valid_representative_name(tag_text)):
                    logger.info(f"[PARSING] Representative: Tìm thấy từ <{tag_name}> trong parent (Cách 1): {tag_text}")
                    return tag_text, f"span-div-p-in-parent-{tag_name}"
        return None, None
    
    def _extract_rep_from_parent_text(self, rep_parent) -> tuple[Optional[str], Optional[str]]:
        """Extract representative từ text của parent (Ưu tiên 4)."""
        rep_text = rep_parent.get_text(separator=" ", strip=True)
        if ":" in rep_text:
            parts = rep_text.split(":", 1)
            if len(parts) > 1:
                candidate = parts[-1].strip()
                candidate = candidate.split("Ngoài ra")[0].strip()
                candidate = candidate.split("còn đại diện")[0].strip()
                if self._is_valid_representative_name(candidate):
                    logger.info(f"[PARSING] Representative: Tìm thấy từ text có dấu ':' (Cách 1): {candidate}")
                    return candidate, "text-with-colon"
        else:
            candidate = rep_text.replace("Người đại diện", "").strip()
            candidate = candidate.split("Ngoài ra")[0].strip()
            if self._is_valid_representative_name(candidate):
                logger.info(f"[PARSING] Representative: Tìm thấy từ text không có dấu ':' (Cách 1): {candidate}")
                return candidate, "text-without-colon"
        return None, None
    
    def _extract_rep_from_sibling(self, rep_parent) -> tuple[Optional[str], Optional[str]]:
        """Extract representative từ next sibling (Ưu tiên 5)."""
        for sibling in rep_parent.next_siblings:
            if hasattr(sibling, 'get_text'):
                sibling_text = sibling.get_text(strip=True)
                if (sibling_text and "Người đại diện" not in sibling_text):
                    candidate = None
                    sib_link = sibling.find("a")
                    if sib_link:
                        candidate = sib_link.get_text(strip=True)
                    else:
                        sib_strong = sibling.find(['strong', 'b'])
                        if sib_strong:
                            candidate = sib_strong.get_text(strip=True)
                        else:
                            candidate = sibling_text
                    
                    if candidate and self._is_valid_representative_name(candidate):
                        logger.info(f"[PARSING] Representative: Tìm thấy từ sibling (Cách 1): {candidate}")
                        return candidate, "next-sibling"
        return None, None
    
    def _extract_rep_from_parent_container(self, rep_parent) -> tuple[Optional[str], Optional[str]]:
        """Extract representative từ parent của parent (Ưu tiên 6)."""
        if not rep_parent.parent:
            return None, None
        
        container = rep_parent.parent
        for tag in container.find_all(['a', 'strong', 'b']):
            tag_text = tag.get_text(strip=True)
            if (tag_text and
                "Người đại diện" not in tag_text and
                self._is_valid_representative_name(tag_text)):
                tag_pos = str(container).find(str(tag))
                label_pos = str(container).find("Người đại diện")
                if tag_pos > label_pos:
                    logger.info(f"[PARSING] Representative: Tìm thấy từ container (Cách 2): {tag_text}")
                    return tag_text, "container-search"
        return None, None
    
    def _extract_rep_from_pattern_matching(self, soup: BeautifulSoup) -> tuple[Optional[str], Optional[str]]:
        """Extract representative từ pattern matching (Cách cuối cùng)."""
        all_text = soup.get_text()
        if "Người đại diện" in all_text:
            idx = all_text.find("Người đại diện")
            after_text = all_text[idx:idx+200]
            if ":" in after_text:
                parts = after_text.split(":", 1)
                if len(parts) > 1:
                    potential_name = parts[1].strip()
                    potential_name = potential_name.split("\n")[0].strip()
                    potential_name = potential_name.split("Ngoài ra")[0].strip()
                    if self._is_valid_representative_name(potential_name):
                        logger.info(f"[PARSING] Representative: Tìm thấy từ pattern matching (Cách 3): {potential_name}")
                        return potential_name, "pattern-matching"
        return None, None
    
    def _clean_representative_name(self, name: str) -> Optional[str]:
        """
        Làm sạch tên người đại diện.
        
        Args:
            name: Tên cần làm sạch
            
        Returns:
            Tên đã làm sạch hoặc None nếu không hợp lệ
        """
        if not name:
            return None
        
        cleaned = name.split("Ngoài ra")[0].strip()
        cleaned = cleaned.split("còn đại diện")[0].strip()
        cleaned = cleaned.split("\n")[0].strip()
        cleaned = cleaned.split("<")[0].strip()
        cleaned = cleaned.strip(".,;: ")
        cleaned = cleaned.split("(")[0].strip()
        
        if cleaned and len(cleaned) > 1 and len(cleaned) < 100:
            return cleaned
        return None
    
    def _parse_address_fallback(self, soup: BeautifulSoup, details: dict) -> None:
        """
        Parse địa chỉ từ HTML (fallback) - tìm riêng "Địa chỉ" không phải "Địa chỉ Thuế".
        Updates details dict in-place.
        """
        if details.get('address'):
            return
        
        address_elem = soup.find(string=lambda s: s and "Địa chỉ" in s and "Địa chỉ Thuế" not in s)
        if address_elem:
            address_parent = address_elem.parent
            address_text = address_parent.get_text(separator=" ", strip=True)
            if ":" in address_text:
                address = address_text.split(":", 1)[-1].strip()
                address = address.replace("Địa chỉ", "").strip()
                if address and address != details.get('tax_address'):
                    details['address'] = address
        
        if not details.get('address') and details.get('tax_address'):
            details['address'] = details['tax_address']
    
    def _parse_phone_fallback(self, soup: BeautifulSoup, details: dict) -> None:
        """
        Parse số điện thoại từ HTML (fallback).
        Updates details dict in-place.
        """
        if details.get('phone'):
            return
        
        phone = self._get_value_by_label(soup, "Điện thoại")
        if phone:
            phone_clean = self._clean_phone_number(phone)
            if phone_clean:
                details['phone'] = phone_clean
    
    def _parse_standard_fields_fallback(self, soup: BeautifulSoup, details: dict) -> None:
        """
        Parse các field chuẩn từ HTML (fallback) - dùng _get_value_by_label.
        Updates details dict in-place.
        """
        if not details.get('tax_code'):
            tax_code = self._get_value_by_label(soup, "Mã số thuế")
            if tax_code:
                details['tax_code'] = tax_code
        
        if not details.get('tax_address'):
            tax_address = self._get_value_by_label(soup, "Địa chỉ Thuế")
            if tax_address:
                details['tax_address'] = tax_address
        
        field_mappings = {
            "Tình trạng": "status",
            "Ngày hoạt động": "operation_date",
            "Quản lý bởi": "managed_by",
            "Loại hình DN": "business_type",
            "Ngành nghề chính": "main_business"
        }
        
        for label, field in field_mappings.items():
            if not details.get(field):
                value = self._get_value_by_label(soup, label)
                if value:
                    details[field] = value
    
    def _parse_by_label_fallback(self, soup: BeautifulSoup, details: dict) -> None:
        """
        Fallback parsing bằng cách tìm theo label - sử dụng khi không parse được từ table.
        Updates details dict in-place.
        """
        self._parse_standard_fields_fallback(soup, details)
        self._parse_address_fallback(soup, details)
        self._parse_representative(soup, details)
        self._parse_phone_fallback(soup, details)
        
        if not details.get('other_businesses'):
            other_businesses_list = self._parse_other_businesses_table(soup)
            if other_businesses_list:
                details['other_businesses'] = other_businesses_list
                logger.debug(f"Tổng cộng {len(other_businesses_list)} ngành nghề khác (fallback)")
    
    def _extract_value_from_td(self, value_td) -> str:
        """
        Lấy giá trị từ value_td - ưu tiên link, sau đó span.copy, cuối cùng là text.
        """
        link = value_td.find('a')
        if link:
            return link.get_text(strip=True)
        
        span = value_td.find('span', class_='copy')
        if span:
            return span.get_text(strip=True)
        
        return value_td.get_text(strip=True)
    
    def _parse_itemprop_fields(self, value_td, details: dict) -> bool:
        """
        Parse các field có itemprop (taxID, address, telephone).
        Returns True nếu đã parse và nên continue (không cần parse label nữa).
        
        Args:
            value_td: BeautifulSoup Tag của td chứa giá trị
            details: Dict để update
            
        Returns:
            True nếu đã parse và nên continue, False nếu chưa parse
        """
        itemprop = value_td.get('itemprop')
        
        if itemprop == 'taxID':
            value = value_td.get_text(strip=True)
            details['tax_code'] = value
            return True
        
        elif itemprop == 'address':
            tax_addr_span = value_td.find(id='tax-address-html')
            if tax_addr_span:
                details['tax_address'] = tax_addr_span.get_text(strip=True)
            else:
                details['address'] = value_td.get_text(strip=True)
            return True
        
        elif itemprop == 'telephone':
            phone_text = value_td.get_text(strip=True)
            has_hidden = ('Bị ẩn' in phone_text or 
                         'ẩn' in phone_text.lower() or
                         value_td.find('em') is not None)
            
            if not has_hidden and phone_text:
                phone_clean = ''.join(c for c in phone_text if c.isdigit() or c in ['+', '-', ' ', '(', ')'])
                phone_clean = phone_clean.strip()
                if phone_clean:
                    details['phone'] = phone_clean
            return True
        
        return False
    
    def _clean_phone_number(self, phone: str) -> Optional[str]:
        """
        Làm sạch số điện thoại - loại bỏ các ký tự không hợp lệ.
        
        Args:
            phone: Số điện thoại gốc
            
        Returns:
            Số điện thoại đã làm sạch, hoặc None nếu không hợp lệ
        """
        if not phone:
            return None
        
        if 'Bị ẩn' in phone or 'ẩn' in phone.lower():
            return None
        
        phone_clean = ''.join(c for c in phone if c.isdigit() or c in ['+', '-', ' ', '(', ')'])
        phone_clean = phone_clean.strip()
        
        return phone_clean if phone_clean else None
    
    def _map_table_row_to_field(self, label_text: str, value: str, value_td, details: dict) -> None:
        """
        Map label text với field name và update details dict.
        
        Args:
            label_text: Text của label
            value: Giá trị đã extract từ value_td
            value_td: BeautifulSoup Tag của td chứa giá trị (để parse representative, phone)
            details: Dict để update
        """
        link = value_td.find('a')
        
        if 'Mã số thuế' in label_text:
            if not details.get('tax_code'):
                details['tax_code'] = value
        elif 'Địa chỉ Thuế' in label_text:
            details['tax_address'] = value
        elif 'Địa chỉ' in label_text and 'Địa chỉ Thuế' not in label_text:
            if not details.get('address'):
                details['address'] = value
        elif 'Tình trạng' in label_text:
            details['status'] = value
        elif 'Người đại diện' in label_text:
            if not details.get('representative'):
                # Tìm trong span với itemprop="name" (cách chính xác nhất)
                name_span = value_td.find('span', itemprop='name')
                if name_span:
                    name_link = name_span.find('a')
                    rep_name = name_link.get_text(strip=True) if name_link else name_span.get_text(strip=True)
                    if rep_name and self._is_valid_representative_name(rep_name):
                        details['representative'] = rep_name
                else:
                    # Fallback: lấy từ link hoặc text
                    rep_name = link.get_text(strip=True) if link else value
                    if rep_name and self._is_valid_representative_name(rep_name):
                        details['representative'] = rep_name
        elif 'Điện thoại' in label_text:
            if not details.get('phone'):
                phone_clean = self._clean_phone_number(value)
                if phone_clean and not value_td.find('em'):
                    details['phone'] = phone_clean
        elif 'Ngày hoạt động' in label_text:
            details['operation_date'] = value
        elif 'Quản lý bởi' in label_text:
            details['managed_by'] = value
        elif 'Loại hình DN' in label_text:
            details['business_type'] = value
        elif 'Ngành nghề chính' in label_text:
            if link:
                details['main_business'] = link.get_text(strip=True)
            else:
                details['main_business'] = value
    
    def _parse_table_row(self, row, details: dict) -> None:
        """
        Parse một row trong table-taxinfo.
        Updates details dict in-place.
        
        Args:
            row: BeautifulSoup Tag của tr
            details: Dict để update
        """
        tds = row.find_all('td')
        if len(tds) < 2:
            return
        
        label_td = tds[0]
        value_td = tds[1]
        label_text = label_td.get_text(strip=True)
        
        if self._parse_itemprop_fields(value_td, details):
            return
        
        value = self._extract_value_from_td(value_td)
        self._map_table_row_to_field(label_text, value, value_td, details)
    
    def _parse_table_taxinfo(self, soup: BeautifulSoup, details: dict) -> bool:
        """
        Parse từ table-taxinfo - ưu tiên cao nhất.
        Returns True nếu parse thành công và có dữ liệu.
        """
        table = soup.find('table', class_='table-taxinfo')
        if not table:
            logger.debug("[PARSING] Method: table-taxinfo - NOT FOUND, sẽ dùng fallback")
            return False
        
        logger.info("[PARSING] Method: table-taxinfo - FOUND, bắt đầu parse từ cấu trúc table")
        fields_before = set(details.keys())
        
        rows_parsed = 0
        for row in table.find_all('tr'):
            if self._parse_table_row(row, details):
                rows_parsed += 1
        
        logger.debug(f"[PARSING] Method: table-taxinfo - Đã parse {rows_parsed} rows")
        
        other_businesses_list = self._parse_other_businesses_table(soup)
        if other_businesses_list:
            details['other_businesses'] = other_businesses_list
            logger.debug(f"[PARSING] Method: table-taxinfo - Tìm thấy {len(other_businesses_list)} ngành nghề khác")
        
        fields_after = set(details.keys())
        new_fields = fields_after - fields_before
        logger.info(f"[PARSING] Method: table-taxinfo - Parse thành công. Fields mới: {sorted(new_fields)}")
        
        return len(details) > 0
    
    def get_company_details(self, detail_url: str) -> Dict[str, Any]:
        """
        Lấy thông tin chi tiết từ trang detail của công ty.
        Parse HTML một cách toàn diện để lấy tất cả thông tin.
        Có sử dụng cache nếu được bật.
        """
        cache_key = extract_tax_code_from_url(detail_url) or detail_url
        if self.cache_enabled and self.file_cache:
            cached_data = self.file_cache.get(cache_key)
            if cached_data:
                logger.debug(f"Cache hit for {cache_key}")
                return cached_data
        
        html, soup = self._get_html_and_soup(detail_url, params={})
        
        details = {}
        
        fields_before_parse = set(details.keys())
        if self._parse_table_taxinfo(soup, details):
            fields_after_parse = set(details.keys())
            new_fields = fields_after_parse - fields_before_parse
            logger.info(
                f"[PARSING] ✅ Method: table-taxinfo - SUCCESS. "
                f"Parse được {len(new_fields)} fields: {sorted(new_fields)}"
            )
        else:
            logger.info("[PARSING] ⚠️ Method: table-taxinfo - FAILED, chuyển sang fallback parsing (by-label)")
            self._parse_by_label_fallback(soup, details)
            fields_after_parse = set(details.keys())
            new_fields = fields_after_parse - fields_before_parse
            logger.info(
                f"[PARSING] ✅ Method: by-label-fallback - COMPLETED. "
                f"Parse được {len(new_fields)} fields: {sorted(new_fields)}"
            )
        
        if self.cache_enabled and self.file_cache:
            self.file_cache.set(cache_key, details)
            logger.debug(f"Cached data for {cache_key}")
        
        return details