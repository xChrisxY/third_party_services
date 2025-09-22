from pydantic import BaseModel, Field 
from typing import Optional, Dict, Any, List 
from datetime import datetime 

class ClientContact(BaseModel):
    name: Optional[str] = None 
    last_names : Optional[str] = None 
    email: Optional[str] = None 
    email2: Optional[str] = None 
    email3: Optional[str] = None 
    phone: Optional[str] = None 