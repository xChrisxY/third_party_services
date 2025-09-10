from abc import ABC, abstractmethod 
from typing import Optional, List 
from ..entities.company import Company 

class CompanyRepository(ABC): 
    
    @abstractmethod
    async def create(self, company: Company) -> Company: 
        pass 
    
    @abstractmethod
    async def get_by_id(self, company_id: str) -> Optional[Company]: 
        pass 
    
    @abstractmethod 
    async def update(self, company: Company) -> Company: 
        pass 
    
    @abstractmethod 
    async def delete(self, company_id: str) -> bool: 
        pass