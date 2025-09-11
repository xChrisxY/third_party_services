from ...domain.repositories.company_repository import CompanyRepository 
from shared.exceptions import NotFoundException

class DeleteCompanyUseCase: 
    
    def __init__(self, company_repository: CompanyRepository): 
        self.company_repository = company_repository 
        
    async def execute(self, company_id: str) -> bool: 
        
        success = await self.company_repository.delete(company_id) 
        
        if not success: 
            raise NotFoundException(f"Company with id {company_id} not found")
        
        return success