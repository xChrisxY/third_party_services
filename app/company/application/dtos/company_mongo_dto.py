from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime
from .company_event_dto import CompanyEventDTO

class CompanyMongoDTO(BaseModel):
    tenant_id: str = Field(..., alias="tenantId")
    business_name: str = Field(..., alias="businessName")
    trade_name: Optional[str] = Field(None, alias="tradeName")
    
    source: Dict[str, Any] = Field(default_factory=dict)
    contact: Dict[str, Any] = Field(default_factory=dict)
    fiscal_data: Dict[str, Any] = Field(..., alias="fiscalData")
    emails: Dict[str, Any] = Field(default_factory=dict)
    configs: Dict[str, Any] = Field(default_factory=dict)
    metadata: Dict[str, Any] = Field(default_factory=dict)
    series: List[Dict[str, Any]] = Field(default_factory=list)

    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }

    @classmethod
    def from_event_dto(
        cls, 
        event_dto: CompanyEventDTO, 
        factura_id: str, 
        credentials: Dict[str, Any],
        company_series: List[Dict[str, Any]]
    ) -> 'CompanyMongoDTO':
        credentials_data = credentials.get('data', {})
        
        fiscal_data = {
            "legalName": event_dto.business_name,
            "taxId": event_dto.tax_id,
            "taxRegime": event_dto.fiscal_data.get('tax_regime') or event_dto.tax_regime,
            "zipCode": event_dto.get_address_field('zip_code') or event_dto.zip_code,
            "street": event_dto.get_address_field('street'),
            "extNumber": event_dto.get_address_field('ext_number') or event_dto.get_address_field('exterior_number'),
            "intNumber": event_dto.get_address_field('int_number') or event_dto.get_address_field('interior_number'),
            "neighborhood": event_dto.get_address_field('neighborhood'),
            "state": event_dto.get_address_field('state'),
            "city": event_dto.get_address_field('city'),
            "country": "México",
            "curp": event_dto.fiscal_data.get('curp'),
            "municipality": event_dto.get_address_field('municipality'),
        }

        contact_email = event_dto.get_email('contact') or ""
        accounting_email = event_dto.get_email('accountant') or event_dto.get_email('accounting') or ""
        
        emails_data = {
            "contact": contact_email,
            "owner": event_dto.get_email('owner') or contact_email,
            "billing": event_dto.get_email('billing') or contact_email,
        }
        
        if accounting_email:
            emails_data["accountant"] = accounting_email
        
        database_data = {
            "tenantId": event_dto.tenant_id,
            "businessName": event_dto.business_name,
            "tradeName": event_dto.trade_name,
            
            "source": {
                "service": "external",
                "serviceId": event_dto.tenant_id,
                "referralCode": None
            },
            
            "contact": {
                "name": event_dto.get_contact_field('name') or "",
                "phone": event_dto.get_contact_field('phone') or "",
                "email": event_dto.get_email('contact') or ""
            },
            
            "fiscalData": {k: v for k, v in fiscal_data.items() if v is not None},
            
            "emails": emails_data,
            
            "configs": {
                "sendCopyToClient": True,
                "sendCopyToAccountant": bool(event_dto.get_email('accountant')),
                "notifications": {
                    "whatsapp": False,
                    "slack": False,
                    "webhookUrl": None
                }
            },
            
            "metadata": {
                "apiKey": credentials_data.get('api_key'),
                "apiSecret": credentials_data.get('secret_key'),
                "thpFcUid": credentials_data.get('uid'),
                "facturaCompanyId": factura_id,
                "createdAt": datetime.now().isoformat(),
                "updatedAt": datetime.now().isoformat(),
                "status": "active"
            },
            
            "series": company_series
        }
        
        return cls(**database_data)
