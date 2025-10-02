from pydantic import BaseModel, Field, field_validator, model_validator
from typing import Optional, Dict, Any, List

class FlexibleModel(BaseModel):
    model_config = {
        "populate_by_name": True,
        "extra": "ignore",
    }

class CompanyEventDTO(FlexibleModel):
    tenant_id: str = Field(..., description="ID único del tenant")
    business_name: str = Field(..., description="Razón social")
    trade_name: Optional[str] = Field(None, description="Nombre comercial")

    rfc: Optional[str] = Field(None, description="RFC")
    tax_id: Optional[str] = Field(None, description="Tax ID")
    tax_regime: Optional[str] = Field(None, description="Régimen fiscal")
    zip_code: Optional[str] = Field(None, description="Código postal")

    fiscal_data: Optional[Dict[str, Any]] = Field(default_factory=dict)
    address: Optional[Dict[str, Any]] = Field(default_factory=dict)
    contact: Optional[Dict[str, Any]] = Field(default_factory=dict)
    emails: Optional[Dict[str, Any]] = Field(default_factory=dict)
    certificates: Optional[Dict[str, Any]] = Field(default_factory=dict)
    smtp_config: Optional[Dict[str, Any]] = Field(default_factory=dict)
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    series: List[Dict[str, Any]] = Field(default_factory=list)

    @model_validator(mode='after')
    def extract_tax_id(self) -> 'CompanyEventDTO':
        if self.tax_id:
            return self
            
        fiscal_data = self.fiscal_data or {}
        if fiscal_data:
            tax_id = fiscal_data.get('tax_id') or fiscal_data.get('rfc')
            if tax_id:
                self.tax_id = tax_id
                return self
        
        if self.rfc:
            self.tax_id = self.rfc
            return self
            
        return self

    def get_email(self, email_type: str) -> Optional[str]:
        emails = self.emails or {}
        contact = self.contact or {}

        if email_type in emails:
            return emails[email_type]
        elif email_type == "contact" and "email" in contact:
            return contact["email"]
        elif email_type == "contact" and "email" in emails:
            return emails["email"]

        return None

    def get_address_field(self, field: str) -> Optional[str]:
        fiscal_data = self.fiscal_data or {}
        address = self.address or {}
        return fiscal_data.get(field) or address.get(field)

    def get_contact_field(self, field: str) -> Optional[str]:
        contact = self.contact or {}
        return contact.get(field)