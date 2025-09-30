from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List 
from datetime import datetime

from .client_address import ClientAddress 
from .client_contact import ClientContact

class Client(BaseModel): 
    id: Optional[str] = Field(default=None, alias="_id")
    tenant_id: str 
    external_uid: Optional[str] = None
    company_id: Optional[str] = Field(None, description="ID de la empresa que factura que factura para este cliente")
    
    rfc: str
    business_name: str
    tax_regime: Optional[str] = None  
    tax_regime_name: Optional[str] = None 
    tax_id_number: Optional[str] = None
    
    address: Optional[ClientAddress] = None
    
    contact: Optional[ClientContact] = None
    
    cfdi_use: Optional[str] = None 
    cfdi_use_name: Optional[str] = None
    
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    status: str = "active" 
    factura_sync: bool = False

    emails: Optional[List[str]] = None 

    model_config = ConfigDict(
            arbitrary_types_allowed=True,
            populate_by_name=True,
            str_strip_whitespace=True,
            validate_assignment=True,
            json_encoders={datetime: lambda v: v.isoformat()},
        )