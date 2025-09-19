from abc import ABC, abstractmethod 
from typing import Any, Dict

class ExternalCompanyRepository(ABC):
    
    @abstractmethod
    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]: 
        pass 
    
    async def get_company_credentials(self, uid: str) -> Dict[str, Any]: 
        pass