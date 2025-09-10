from ...domain.entities.company import Company
from ...domain.repositories.company_repository import CompanyRepository
from ..dtos.create_company_dto import CreateCompanyDTO

from shared.exceptions import BusinessException

class CreateCompanyUseCase: 
    
    def __init__(self, company_repository: CompanyRepository): 
        self.company_repository = company_repository 
        
    async def execute(self, company_dto: CreateCompanyDTO) -> Company: 
        
        try: 

            company = Company(
                tenant_id=company_dto.tenant_id, 
                business_name=company_dto.business_name, 
                trade_name=company_dto.trade_name, 
                source=company_dto.source, 
                contact=company_dto.contact, 
                fiscal_data=company_dto.fiscal_data, 
                emails=company_dto.emails, 
                configs=company_dto.configs, 
                metadata=company_dto.metadata
            )
            
            created_company = await self.company_repository.create(company)

            return created_company

        except Exception as e: 
            raise BusinessException(f"Failed to create company: {str(e)}")