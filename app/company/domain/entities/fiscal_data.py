from pydantic import BaseModel, Field 
from typing import Optional, Dict 

class FiscalData(BaseModel): 
    legal_name: str = Field(..., alias="legalName")
    tax_id: str = Field(..., alias="taxId")
    tax_regime: str = Field(..., alias="taxRegime")
    zip_code: str = Field(..., alias="zipCode")
    street: str 
    ext_number: str = Field(..., alias="extNumber")
    int_number: Optional[str] = Field(None, alias="intNumber")
    neighborhood: str 
    state: str 
    city: str 
    country: str 
    curp: Optional[str] = Field(None, description="CURP de la empresa")
    
    class Config: 
        populate_by_name = True 
        extra = "allow"