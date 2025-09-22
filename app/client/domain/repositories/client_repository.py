from abc import ABC, abstractmethod 
from typing import Optional, List 
from ..entities.client import Client 

class ClientRepository(ABC):
    
    @abstractmethod 
    async def create(self, client: Client) -> Client:
        pass 

    @abstractmethod 
    async def get_by_id(self, client_id: str) -> Optional[Client]:
        pass
    
    
