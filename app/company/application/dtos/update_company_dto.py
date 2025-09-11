from typing import Optional, Any, Dict
from pydantic import BaseModel, Field, model_validator
from ...domain.entities.company import Source, Contact, FiscalData, Configs
from ..dtos.update_email_dto import UpdateEmailsDTO

class UpdateCompanyDTO(BaseModel):
    tenant_id: Optional[str] = Field(None, alias="tenantId")
    business_name: Optional[str] = Field(None, alias="businessName")
    trade_name: Optional[str] = Field(None, alias="tradeName")
    
    source: Optional[Source] = None
    contact: Optional[Contact] = None
    fiscal_data: Optional[FiscalData] = Field(None, alias="fiscalData")
    emails: Optional[UpdateEmailsDTO] = None
    configs: Optional[Configs] = None

    class Config:
        populate_by_name = True
        extra = "forbid"