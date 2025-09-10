from typing import Optional 
from pydantic import field_validator 
from ...domain.entities.company import Company 

class CreateCompanyDTO(Company): 
    
    id: Optional[str] = None 
    metatada: Optional[dict] = None 
    
    @field_validator('tenant_id', 'business_name')
    def validate_required_fields(cls, v): 
        if not v or not v.strip(): 
            raise ValueError('Field cannot be empty')
        return v.strip()

    class Config: 
        pupulate_by_name = True