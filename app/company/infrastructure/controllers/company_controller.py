from typing import List 
from fastapi import HTTPException, status 

from ...application.use_cases.create_company_use_case import CreateCompanyUseCase 

from ...application.dtos.create_company_dto import CreateCompanyDTO
from ...application.dtos.company_response import CompanyResponseDTO

from shared.responses import SuccessResponse
from shared.exceptions import BusinessException

class CompanyController: 
    def __init__(self, create_company_use_case: CreateCompanyUseCase): 
        self.create_company_use_case = create_company_use_case 
        
    async def create_company(self, company_dto: CreateCompanyDTO) -> SuccessResponse:
        
        try: 
            
            company = await self.create_company_use_case.execute(company_dto)
            
            company_response = CompanyResponseDTO(
                tenant_id=company.tenant_id, 
                business_name=company.business_name, 
                trade_name=company.trade_name, 
                source=company.source, 
                contact=company.contact, 
                fiscal_data=company.fiscal_data, 
                emails=company.emails, 
                configs=company.configs, 
                metadata=company.metadata
            )

            return SuccessResponse(
                data=company_response, 
                message="Company created successfully", 
                status_code=status.HTTP_201_CREATED
            )
        
        except BusinessException as e: 
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail=str(e)
            )

        except Exception as e: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Internal Server Error: {str(e)}"
            )