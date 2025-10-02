from pydantic import BaseModel, Field
from typing import Optional, Literal 

class Source(BaseModel): 
    service: Literal["inventix", "foodix", "external"] = Field(..., description="Source service")
    service_id: str = Field(..., alias="serviceId", description="ID of the client in the source system")
    referral_code: Optional[str] = Field(None, alias="referralCode", description="Optional referral tracking  code")

    class Config: 
        populate_by_name = True 
        extra = "allow"