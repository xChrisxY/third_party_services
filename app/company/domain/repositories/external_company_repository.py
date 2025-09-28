from abc import ABC, abstractmethod 
from typing import Any, Dict, Optional, List

class ExternalCompanyRepository(ABC):
    
    @abstractmethod
    async def create_company(self, company_data: Dict[str, Any]) -> Dict[str, Any]: 
        pass 
    
    @abstractmethod
    async def get_company_credentials(self, uid: str) -> Dict[str, Any]: 
        pass

    @abstractmethod
    async def get_all_series(self) -> List[Dict[str, Any]]: 
        pass

    @abstractmethod
    async def get_default_series(self, company_uid: str) -> Optional[Dict[str, Any]]:
        pass 

    @abstractmethod
    async def get_series_by_name(self, series_name: str) -> Optional[Dict[str, Any]]: 
        pass
    
    @abstractmethod
    async def create_series(self, company_uid: str, series_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        pass 
    