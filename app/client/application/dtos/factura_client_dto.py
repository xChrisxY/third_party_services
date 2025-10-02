from pydantic import BaseModel, Field
from typing import Optional
from .client_event_dto import ClientEventDTO

class FacturaClientDTO(BaseModel):
    
    rfc: str = Field(..., description="RFC del cliente")
    razons: str = Field(..., description="Razón social")
    codpos: str = Field(..., description="Código postal")
    email: str = Field(..., description="Email principal")
    regimen: str = Field(..., description="Régimen fiscal")
    pais: str = Field(default="MEX", description="País")
    
    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None
    colonia: Optional[str] = None
    ciudad: Optional[str] = None
    delegacion: Optional[str] = None
    localidad: Optional[str] = None
    estado: Optional[str] = None
    
    nombre: Optional[str] = None
    apellidos: Optional[str] = None
    telefono: Optional[str] = None
    email2: Optional[str] = None
    email3: Optional[str] = None
    
    usocfdi: Optional[str] = None
    numregidtrib: Optional[str] = None

    model_config = {
        "populate_by_name": True,
        "extra": "ignore"
    }

    @classmethod
    def from_event_dto(cls, event_dto: ClientEventDTO) -> 'FacturaClientDTO':

        factura_data = {
            "rfc": event_dto.rfc,
            "razons": event_dto.business_name,
            "codpos": event_dto.get_address_field('zip_code') or "",
            "email": event_dto.get_email('email') or "",
            "regimen": event_dto.tax_regime or "603",
            "pais": event_dto.get_address_field('country') or "MEX",
        }
        
        address_mapping = {
            "calle": event_dto.get_address_field('street'),
            "numero_exterior": event_dto.get_address_field('exterior_number'),
            "numero_interior": event_dto.get_address_field('interior_number'),
            "colonia": event_dto.get_address_field('neighborhood'),
            "ciudad": event_dto.get_address_field('city'),
            "delegacion": event_dto.get_address_field('municipality'),
            "localidad": event_dto.get_address_field('locality'),
            "estado": event_dto.get_address_field('state'),
        }
        
        contact_mapping = {
            "nombre": event_dto.get_contact_field('name'),
            "apellidos": event_dto.get_contact_field('last_names'),
            "telefono": event_dto.get_contact_field('phone'),
            "email2": event_dto.get_email('email2'),
            "email3": event_dto.get_email('email3'),
        }
        
        fiscal_mapping = {
            "usocfdi": event_dto.cfdi_use,
            "numregidtrib": event_dto.tax_id_number,
        }
        
        factura_data.update(address_mapping)
        factura_data.update(contact_mapping)
        factura_data.update(fiscal_mapping)
        
        return cls(**{k: v for k, v in factura_data.items() if v is not None and v != ""})