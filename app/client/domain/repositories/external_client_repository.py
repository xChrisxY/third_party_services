from abc import ABC, abstractmethod
from typing import List, Dict, Any

class ExternalClientRepository(ABC): 
    
    @abstractmethod 
    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        pass 
    
    @abstractmethod 
    async def get_client_by_id(self, uid: str) -> Dict[str, Any]:
        pass 

    @abstractmethod
    async def get_cfdi_uses(self) -> List[Dict[str, Any]]:
        pass 
    
    @abstractmethod 
    async def get_tax_regimes(self) -> List[Dict[str, Any]]:
        pass 
    
    @abstractmethod
    async def get_countries(self) -> List[Dict[str, Any]]: 
        pass 
    
    @abstractmethod 
    async def validate_cfdi_use(self, cfdi_use: str, tax_regime: str = None) -> Dict[str, Any]:
        pass 
    
    @abstractmethod
    async def validate_tax_regime(self, regime_code: str) -> Dict[str, Any]:
        pass 
    
    @abstractmethod
    async def validate_country(self, country_code: str) -> bool:
        pass 
    