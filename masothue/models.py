# models.py
# -*- coding: utf-8 -*-

from dataclasses import dataclass
from typing import Optional, List, Union


@dataclass
class CompanySearchResult:
    """
    Kết quả tìm kiếm công ty từ masothue.com
    
    Note: other_businesses có thể là list (từ client mới) hoặc string (từ cache cũ).
    Formatters sẽ xử lý cả 2 trường hợp.
    """
    name: str
    tax_code: str
    representative: Optional[str]
    address: Optional[str]
    detail_url: Optional[str]
    tax_address: Optional[str] = None  # Địa chỉ Thuế
    phone: Optional[str] = None
    status: Optional[str] = None
    operation_date: Optional[str] = None
    managed_by: Optional[str] = None
    business_type: Optional[str] = None
    main_business: Optional[str] = None
    other_businesses: Union[Optional[str], Optional[List[str]]] = None  

