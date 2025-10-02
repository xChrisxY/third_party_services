from pydantic import BaseModel, Field
from typing import Optional, List

from .source import Source 
from .fiscal_data import FiscalData 
from .emails import Emails 
from .contact import Contact 
from .configs import Configs
from .metadata import Metadata
from .series import Series

class Company(BaseModel): 
    id: Optional[str] = Field(None, alias="_id", description="ObjectId")
    tenant_id: str = Field(..., alias="tenantId", description="Unique tenant identifier")
    business_name: str = Field(..., alias="businessName", description="Registered business name")
    trade_name: Optional[str] = Field(None, alias="tradeName", description="Optional commercial name")

    source: Source 
    contact: Contact 
    fiscal_data: FiscalData = Field(..., alias="fiscalData")
    emails: Emails 
    configs: Configs 
    metadata: Metadata
    series: List[Series] = Field(default=[], description="Billing series list")

    class Config: 
        populate_by_name = True 
        extra = "allow"

