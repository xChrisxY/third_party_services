from pydantic import BaseModel, Field 
from typing import Optional 

class ClientAddress(BaseModel):
    street: Optional[str] = None 
    exterior_number: Optional[str] = None 
    interior_number: Optional[str] = None 
    neighborhood: Optional[str] = None 
    zip_code: Optional[str] = None 
    city: Optional[str] = None 
    municipality: Optional[str] = None 
    locality: Optional[str] = None 
    state: Optional[str] = None 
    country: Optional[str] = None 
    
    
    