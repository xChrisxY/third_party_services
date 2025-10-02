from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from .client_event_dto import ClientEventDTO

class ClientMongoDTO(BaseModel):
    
    tenant_id: str = Field(..., alias="tenantId")
    external_uid: str = Field(..., alias="externalUid", description="UID de Factura.com")
    company_id: Optional[str] = Field(None, alias="companyId")
    
    rfc: str
    business_name: str = Field(..., alias="businessName")
    
    tax_regime: Optional[str] = Field(None, alias="taxRegime")
    tax_regime_name: Optional[str] = Field(None, alias="taxRegimeName")
    tax_id_number: Optional[str] = Field(None, alias="taxIdNumber")
    
    address: Dict[str, Any] = Field(default_factory=dict)
    contact: Dict[str, Any] = Field(default_factory=dict)
    
    cfdi_use: Optional[str] = Field(None, alias="cfdiUse")
    cfdi_use_name: Optional[str] = Field(None, alias="cfdiUseName")
    
    emails: Optional[List[str]] = None
    
    created_at: datetime = Field(default_factory=datetime.now, alias="createdAt")
    updated_at: datetime = Field(default_factory=datetime.now, alias="updatedAt")
    status: str = "active"
    factura_sync: bool = Field(default=True, alias="facturaSync")

    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }

    @classmethod
    def from_event_dto(
        cls,
        event_dto: ClientEventDTO,
        factura_uid: str,
        factura_response: Optional[Dict[str, Any]] = None,
        tax_regime_name: Optional[str] = None,
        cfdi_use_name: Optional[str] = None
    ) -> 'ClientMongoDTO':
        
        address_data = {
            "street": event_dto.get_address_field('street'),
            "exteriorNumber": event_dto.get_address_field('exterior_number'),
            "interiorNumber": event_dto.get_address_field('interior_number'),
            "neighborhood": event_dto.get_address_field('neighborhood'),
            "zipCode": event_dto.get_address_field('zip_code'),
            "city": event_dto.get_address_field('city'),
            "municipality": event_dto.get_address_field('municipality'),
            "locality": event_dto.get_address_field('locality'),
            "state": event_dto.get_address_field('state'),
            "country": event_dto.get_address_field('country') or "MEX",
        }
        
        address_data = {k: v for k, v in address_data.items() if v is not None}
        
        contact_data = {
            "name": event_dto.get_contact_field('name'),
            "lastNames": event_dto.get_contact_field('last_names'),
            "email": event_dto.get_email('email'),
            "email2": event_dto.get_email('email2'),
            "email3": event_dto.get_email('email3'),
            "phone": event_dto.get_contact_field('phone'),
        }
        
        contact_data = {k: v for k, v in contact_data.items() if v is not None}
        
        emails = event_dto.get_all_emails()
        
        mongo_data = {
            "tenantId": event_dto.tenant_id,
            "externalUid": factura_uid,
            "companyId": event_dto.company_id,
            "rfc": event_dto.rfc,
            "businessName": event_dto.business_name,
            "taxRegime": event_dto.tax_regime,
            "taxRegimeName": tax_regime_name,
            "taxIdNumber": event_dto.tax_id_number,
            "address": address_data,
            "contact": contact_data,
            "cfdiUse": event_dto.cfdi_use,
            "cfdiUseName": cfdi_use_name,
            "emails": emails if emails else None,
            "createdAt": datetime.now(),
            "updatedAt": datetime.now(),
            "status": "active",
            "facturaSync": True,
        }
        
        return cls(**{k: v for k, v in mongo_data.items() if v is not None})