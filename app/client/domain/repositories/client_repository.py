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

    @abstractmethod 
    async def find_by_rfc(self, client_rfc: str) -> Optional[Client]:
        pass

    @abstractmethod
    async def find_by_company(self, rfc: str, company_id: str) -> Optional[Client]:
        pass
    
    
