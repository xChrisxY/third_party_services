from pydantic import BaseModel, Field 
from typing import Optional 

class Notifications(BaseModel):
    whatsapp: bool = False 
    slack: bool = False 
    webhook_url: Optional[str] = Field(None, alias="webhookUrl")

    class Config: 
        populate_by_name = True 
        extra = "allow"


class Configs(BaseModel): 
    send_copy_to_client: bool = Field(..., alias="sendCopyToClient")
    send_copy_to_accountant: bool = Field(..., alias="sendCopyToAccountant")
    notifications: Notifications 
    
    class Config: 
        populate_by_name = True 
        extra = "allow"