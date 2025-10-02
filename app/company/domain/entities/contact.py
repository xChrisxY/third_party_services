from pydantic import BaseModel, EmailStr

class Contact(BaseModel):
    name: str 
    phone: str 
    email: EmailStr

    class Config:
        extra = "allow"