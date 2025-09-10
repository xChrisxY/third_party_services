from typing import Generic, TypeVar, Optional, Any 
from pydantic import BaseModel 

T = TypeVar('T')

class SuccessResponse(BaseModel, Generic[T]): 
    success: bool = True 
    data: T 
    message: str 
    status_code: int = 200

    class Config: 
        from_attributes = True

class ErrorResponse(BaseModel): 
    success: bool = False 
    error: str 
    message: str 
    status_code: int 
    details: Optional[Any] = None 
    
    class Config: 
        from_attributes = True