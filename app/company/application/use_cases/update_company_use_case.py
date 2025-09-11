from ...domain.entities.company import Company 
from ...domain.repositories.company_repository import CompanyRepository 
from ..dtos.update_company_dto import UpdateCompanyDTO
from shared.exceptions import NotFoundException

class UpdateCompanyUseCase: 
    
    def __init__(self, company_repository: CompanyRepository): 
        self.company_repository = company_repository 

    async def execute(self, company_id: str, updated_data: UpdateCompanyDTO) -> Company:
        
        company = await self.company_repository.get_by_id(company_id)
        
        if not company:
            raise NotFoundException(f"Company with id {company_id} not found")

        updated_dict = updated_data.model_dump(exclude_unset=True, by_alias=True)

        updated_company = await self.company_repository.update(company_id, updated_dict)

        return updated_company
        
        
        
        