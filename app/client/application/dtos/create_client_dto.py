from typing import Optional
from pydantic import field_validator
from ...domain.entities.client import Client 

class CreateClientDTO(Client):
    
    id: Optional[str] = None 
    metadata: Optional[dict] = None 
    
    @field_validator('tenant_id')
    def validate_required_fields(cls, v):
        if not v or not v.strip(): 
            raise ValueError('Field cannot be empty')
        return v.strip()

    class Config: 
        pupulate_by_name = True