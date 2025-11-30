# formatters.py
# -*- coding: utf-8 -*-

"""
Helper functions để format dữ liệu cho UI display.
Tách biệt business logic (models) khỏi presentation logic (formatting).
"""

from typing import List, Optional, Dict, Any
from masothue.models import CompanySearchResult


def format_other_businesses(businesses: List[str]) -> str:
    """
    Format danh sách ngành nghề khác thành string để hiển thị (mỗi ngành một dòng).
    
    Args:
        businesses: List các ngành nghề
        
    Returns:
        String với các ngành nghề được join bằng \n, hoặc "" nếu rỗng
    """
    if not businesses:
        return ""
    filtered = [b.strip() for b in businesses if b and b.strip()]
    if not filtered:
        return ""
    return "\n".join(filtered)


def format_phone_number(phone: Optional[str]) -> str:
    """
    Format số điện thoại - giữ nguyên format gốc.
    
    Args:
        phone: Số điện thoại gốc
        
    Returns:
        Số điện thoại đã format, hoặc "" nếu None/rỗng
    """
    if not phone:
        return ""
    return phone.strip()


def result_to_dict(result: CompanySearchResult, query: Optional[str] = None) -> Dict[str, str]:
    """
    Chuyển CompanySearchResult thành dict để hiển thị trong UI/Excel.
    Tất cả formatting cho UI được xử lý ở đây.
    
    Args:
        result: CompanySearchResult từ client
        query: Query gốc (nếu có, để lưu trong batch results)
        
    Returns:
        Dict với keys là tên cột và values là string đã format
    """
    data = {}
    
    if query:
        data["Query"] = query
    
    data["Tên công ty"] = result.name or ""
    data["Mã số thuế"] = result.tax_code or ""
    data["Địa chỉ Thuế"] = result.tax_address or ""
    data["Địa chỉ"] = result.address or ""
    data["Người đại diện"] = result.representative or ""
    data["Điện thoại"] = format_phone_number(result.phone)
    data["Tình trạng"] = result.status or ""
    data["Ngày hoạt động"] = result.operation_date or ""
    data["Quản lý bởi"] = result.managed_by or ""
    data["Loại hình DN"] = result.business_type or ""
    data["Ngành nghề chính"] = result.main_business or ""
    
    if isinstance(result.other_businesses, list):
        data["Ngành nghề khác"] = format_other_businesses(result.other_businesses)
    elif isinstance(result.other_businesses, str):
        data["Ngành nghề khác"] = result.other_businesses
    else:
        data["Ngành nghề khác"] = ""
    
    data["URL"] = result.detail_url or ""
    
    return data


def create_empty_result_dict(query: Optional[str] = None) -> Dict[str, str]:
    """
    Tạo dict rỗng cho kết quả không tìm thấy hoặc lỗi.
    
    Args:
        query: Query gốc (nếu có)
        
    Returns:
        Dict với tất cả fields là rỗng
    """
    data = {}
    
    if query:
        data["Query"] = query
    
    data["Tên công ty"] = ""
    data["Mã số thuế"] = ""
    data["Địa chỉ Thuế"] = ""
    data["Địa chỉ"] = ""
    data["Người đại diện"] = ""
    data["Điện thoại"] = ""
    data["Tình trạng"] = ""
    data["Ngày hoạt động"] = ""
    data["Quản lý bởi"] = ""
    data["Loại hình DN"] = ""
    data["Ngành nghề chính"] = ""
    data["Ngành nghề khác"] = ""
    data["URL"] = ""
    
    return data


def create_error_result_dict(query: str, error_message: str) -> Dict[str, str]:
    """
    Tạo dict cho kết quả lỗi.
    
    Args:
        query: Query gốc
        error_message: Thông báo lỗi
        
    Returns:
        Dict với Tên công ty = "Lỗi: {error_message}", các fields khác rỗng
    """
    data = create_empty_result_dict(query)
    data["Tên công ty"] = f"Lỗi: {error_message}"
    return data


def make_result_row(
    query: str,
    result: Optional[CompanySearchResult] = None,
    details: Optional[Dict[str, Any]] = None,
    error: Optional[str] = None
) -> Dict[str, str]:  # BatchResultDict - Dict với keys có spaces
    """
    Tạo dict cho một dòng kết quả batch search - dùng chung cho GUI và CLI.
    Đảm bảo tất cả các dòng có cùng cấu trúc, tránh thiếu/thừa cột.
    
    Args:
        query: Query gốc (bắt buộc)
        result: CompanySearchResult từ search_companies() (nếu có)
        details: Dict chi tiết từ get_company_details() (nếu có)
        error: Thông báo lỗi (nếu có)
        
    Returns:
        Dict với đầy đủ các keys: Query, Tên công ty, Mã số thuế, ...
        Tất cả keys luôn có, giá trị rỗng nếu không có dữ liệu
    """
    base = {
        "Query": query,
        "Tên công ty": "",
        "Mã số thuế": "",
        "Địa chỉ Thuế": "",
        "Địa chỉ": "",
        "Người đại diện": "",
        "Điện thoại": "",
        "Tình trạng": "",
        "Ngày hoạt động": "",
        "Quản lý bởi": "",
        "Loại hình DN": "",
        "Ngành nghề chính": "",
        "Ngành nghề khác": "",
        "URL": "",
        "Lỗi": ""
    }
    
    if error:
        base["Tên công ty"] = f"Lỗi: {error}"
        base["Lỗi"] = error
        return base
    
    if not result:
        return base
    
    base["Tên công ty"] = result.name or ""
    base["Mã số thuế"] = result.tax_code or ""
    base["Địa chỉ Thuế"] = result.tax_address or ""
    base["Địa chỉ"] = result.address or ""
    base["Người đại diện"] = result.representative or ""
    base["Điện thoại"] = format_phone_number(result.phone)
    base["Tình trạng"] = result.status or ""
    base["Ngày hoạt động"] = result.operation_date or ""
    base["Quản lý bởi"] = result.managed_by or ""
    base["Loại hình DN"] = result.business_type or ""
    base["Ngành nghề chính"] = result.main_business or ""
    
    if isinstance(result.other_businesses, list):
        base["Ngành nghề khác"] = format_other_businesses(result.other_businesses)
    elif isinstance(result.other_businesses, str):
        base["Ngành nghề khác"] = result.other_businesses
    else:
        base["Ngành nghề khác"] = ""
    
    base["URL"] = result.detail_url or ""
    
    if details:
        if details.get('representative'):
            base["Người đại diện"] = details['representative']
        if details.get('tax_address'):
            base["Địa chỉ Thuế"] = details['tax_address']
        if details.get('address'):
            base["Địa chỉ"] = details['address']
        if details.get('phone'):
            base["Điện thoại"] = format_phone_number(details['phone'])
        if details.get('status'):
            base["Tình trạng"] = details['status']
        if details.get('operation_date'):
            base["Ngày hoạt động"] = details['operation_date']
        if details.get('managed_by'):
            base["Quản lý bởi"] = details['managed_by']
        if details.get('business_type'):
            base["Loại hình DN"] = details['business_type']
        if details.get('main_business'):
            base["Ngành nghề chính"] = details['main_business']
        if details.get('other_businesses'):
            if isinstance(details['other_businesses'], list):
                base["Ngành nghề khác"] = format_other_businesses(details['other_businesses'])
            elif isinstance(details['other_businesses'], str):
                base["Ngành nghề khác"] = details['other_businesses']
    
    return base


def format_company_details(details: Dict[str, Any]) -> str:
    """
    Format thông tin chi tiết công ty thành string để hiển thị trong CLI.
    
    Args:
        details: Dict chứa thông tin chi tiết từ get_company_details()
        
    Returns:
        String đã format với các thông tin công ty
    """
    lines = []
    
    if details.get('tax_code'):
        lines.append(f"Mã số thuế: {details['tax_code']}")
    
    if details.get('name'):
        lines.append(f"Tên công ty: {details['name']}")
    
    if details.get('representative'):
        lines.append(f"Người đại diện: {details['representative']}")
    
    if details.get('tax_address'):
        lines.append(f"Địa chỉ Thuế: {details['tax_address']}")
    
    if details.get('address'):
        lines.append(f"Địa chỉ: {details['address']}")
    
    if details.get('phone'):
        lines.append(f"Điện thoại: {details['phone']}")
    
    if details.get('status'):
        lines.append(f"Tình trạng: {details['status']}")
    
    if details.get('operation_date'):
        lines.append(f"Ngày hoạt động: {details['operation_date']}")
    
    if details.get('managed_by'):
        lines.append(f"Quản lý bởi: {details['managed_by']}")
    
    if details.get('business_type'):
        lines.append(f"Loại hình DN: {details['business_type']}")
    
    if details.get('main_business'):
        lines.append(f"Ngành nghề chính: {details['main_business']}")
    
    if details.get('other_businesses'):
        other_businesses = details['other_businesses']
        if isinstance(other_businesses, list):
            lines.append(f"Ngành nghề khác ({len(other_businesses)}):")
            for business in other_businesses:
                lines.append(f"  - {business}")
        elif isinstance(other_businesses, str):
            lines.append(f"Ngành nghề khác: {other_businesses}")
    
    return "\n".join(lines) if lines else "Không có thông tin chi tiết"

