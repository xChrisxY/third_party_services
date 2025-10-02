from pydantic import BaseModel, Field, field_validator
from typing import Optional, Dict, Any
from .company_event_dto import CompanyEventDTO

class FacturaCompanyDTO(BaseModel):
    razons: str = Field(..., description="Razón social")
    rfc: str = Field(..., description="RFC")
    codpos: str = Field(..., description="Código postal")
    email: str = Field(..., description="Email principal")
    
    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None
    colonia: Optional[str] = None
    estado: Optional[str] = None
    ciudad: Optional[str] = None
    delegacion: Optional[str] = None
    regimen: Optional[str] = None
    mailtomyconta: Optional[str] = None
    mail_conta: Optional[str] = None
    mailtomyself: Optional[str] = None
    regimen_nomina: Optional[str] = None
    cant_folios_min: Optional[str] = None
    smtp: Optional[str] = None
    smtp_email: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_port: Optional[str] = None
    smtp_host: Optional[str] = None
    smtp_encryption: Optional[str] = None
    telefono: Optional[str] = None
    curp: Optional[str] = None
    logo: Optional[str] = None
    password: Optional[str] = None
    fiel_cer_b64: Optional[str] = None
    fiel_key_b64: Optional[str] = None
    fielpassword: Optional[str] = None
    csd_cer_b64: Optional[str] = None
    csd_key_b64: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }

    @field_validator('mailtomyconta', 'mailtomyself', 'smtp', mode="before")
    def convert_boolean_to_string(cls, v):
        if isinstance(v, bool):
            return "1" if v else "0"
        return v

    @classmethod
    def from_event_dto(cls, event_dto: CompanyEventDTO) -> 'FacturaCompanyDTO':
        fiscal_data = event_dto.fiscal_data or {}
        certificates = event_dto.certificates or {}
        smtp_config = event_dto.smtp_config or {}
        
        factura_data = {
            "razons": event_dto.business_name,
            "rfc": event_dto.tax_id, 
            "codpos": event_dto.get_address_field('zip_code') or event_dto.zip_code,
            "email": event_dto.get_email('contact'),
            
            "calle": event_dto.get_address_field('street'),
            "numero_exterior": event_dto.get_address_field('ext_number') or event_dto.get_address_field('exterior_number'),
            "numero_interior": event_dto.get_address_field('int_number') or event_dto.get_address_field('interior_number'),
            "colonia": event_dto.get_address_field('neighborhood'),
            "estado": event_dto.get_address_field('state'),
            "ciudad": event_dto.get_address_field('city'),
            "delegacion": event_dto.get_address_field('municipality'),
            
            "regimen": fiscal_data.get('tax_regime') or event_dto.tax_regime,
            "telefono": event_dto.get_contact_field('phone'),
            "curp": fiscal_data.get('curp'),
            
            "mailtomyconta": "1" if event_dto.get_email('accountant') else "0",
            "mail_conta": event_dto.get_email('accountant'),
            "mailtomyself": "1",
            
            "password": certificates.get('fiel_password', '12345678a'),
        }
        
        if certificates.get('fiel_cer'):
            factura_data["fiel_cer_b64"] = certificates['fiel_cer']
        if certificates.get('fiel_key'):
            factura_data["fiel_key_b64"] = certificates['fiel_key']
        if certificates.get('csd_cer'):
            factura_data["csd_cer_b64"] = certificates['csd_cer']
        if certificates.get('csd_key'):
            factura_data["csd_key_b64"] = certificates['csd_key']
        if certificates.get('fiel_password'):
            factura_data["fielpassword"] = certificates['fiel_password']
        
        if smtp_config:
            factura_data.update({
                "smtp": "1",
                "smtp_email": smtp_config.get("email"),
                "smtp_password": smtp_config.get("password"),
                "smtp_port": smtp_config.get("port"),
                "smtp_host": smtp_config.get("host"),
                "smtp_encryption": smtp_config.get("encryption", "tls"),
            })
        else:
            factura_data["smtp"] = "0"
        
        return cls(**{k: v for k, v in factura_data.items() if v is not None})
