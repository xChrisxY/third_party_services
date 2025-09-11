from typing import Optional
from pydantic import EmailStr, BaseModel

class UpdateEmailsDTO(BaseModel):
    contact: Optional[EmailStr] = None
    owner: Optional[EmailStr] = None
    billing: Optional[EmailStr] = None
    accountant: Optional[EmailStr] = None

    class Config:
        extra = "forbid"