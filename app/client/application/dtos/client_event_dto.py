from pydantic import BaseModel, Field, model_validator
from typing import Optional, Dict, Any

class FlexibleModel(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }

class ClientEventDTO(FlexibleModel):
    tenant_id: str = Field(..., description="ID único del tenant")
    company_id: Optional[str] = Field(None, description="ID de la empresa asociada")
    
    rfc: str = Field(..., description="RFC del cliente")
    business_name: str = Field(..., description="Razón social del cliente")
    
    tax_regime: Optional[str] = Field(None, description="Régimen fiscal")
    tax_id_number: Optional[str] = Field(None, description="Número de identificación tributaria")
    cfdi_use: Optional[str] = Field(None, description="Uso de CFDI")
    
    address: Optional[Dict[str, Any]] = Field(default_factory=dict)
    contact: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)

    @model_validator(mode='after')
    def set_defaults(self) -> 'ClientEventDTO':
        if not self.tax_regime:
            self.tax_regime = "603"
        
        if not self.cfdi_use:
            self.cfdi_use = "G03" 
        
        address = self.address or {}
        if not address.get('country'):
            self.address['country'] = "MEX"
        
        return self

    def get_address_field(self, field: str) -> Optional[str]:
        address = self.address or {}
        return address.get(field)

    def get_contact_field(self, field: str) -> Optional[str]:
        contact = self.contact or {}
        return contact.get(field)

    def get_email(self, email_type: str = "email") -> Optional[str]:
        contact = self.contact or {}
        return contact.get(email_type)

    def get_all_emails(self) -> list[str]:
        emails = []
        contact = self.contact or {}
        
        for email_field in ['email', 'email2', 'email3']:
            email = contact.get(email_field)
            if email:
                emails.append(email)
        
        return emails