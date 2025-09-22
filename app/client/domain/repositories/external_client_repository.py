from abc import ABC, abstractmethod
from typing import Dict, Any

class ExternalClientRepository(ABC): 
    
    @abstractmethod 
    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        pass 
    
    @abstractmethod 
    async def get_client_by_id(self, uid: str) -> Dict[str, Any]:
        pass 
    
    