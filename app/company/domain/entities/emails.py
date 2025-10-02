from pydantic import BaseModel, EmailStr 

class Emails(BaseModel): 
    contact: EmailStr 
    owner: EmailStr 
    billing: EmailStr 
    accountant: EmailStr  

    class Config: 
        extra = "allow"
    