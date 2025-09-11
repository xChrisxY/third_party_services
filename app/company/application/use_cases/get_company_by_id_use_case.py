from ...domain.entities.company import Company
from ...domain.repositories.company_repository import CompanyRepository 
from shared.exceptions import NotFoundException 

class GetCompanyByIdUseCase: 
    
    def __init__(self, company_repository: CompanyRepository): 
        self.company_repository = company_repository 
        
    async def execute(self, company_id: str) -> Company: 
        
        company = await self.company_repository.get_by_id(company_id) 
        
        if not company: 
            raise NotFoundException(f"Company with id {company_id} not found")

        return company