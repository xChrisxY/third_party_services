from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime

class Metadata(BaseModel): 
    api_key: str = Field(..., alias="apiKey")
    api_secret: str = Field(..., alias="apiSecret")
    thp_fc_uid: str = Field(..., alias="thpFcUid")
    created_at: datetime = Field(..., alias="createdAt")
    updatedAt: datetime = Field(..., alias="updatedAt")
    status: Literal["active", "inactive", "suspended"]

    class Config: 
        populate_by_name = True 
        extra = "forbid"