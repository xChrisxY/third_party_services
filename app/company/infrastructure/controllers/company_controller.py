from fastapi import HTTPException, status 

from ...domain.entities.company import Company

from ...application.use_cases.create_company_use_case import CreateCompanyUseCase 
from ...application.use_cases.get_company_by_id_use_case import GetCompanyByIdUseCase
from ...application.use_cases.update_company_use_case import UpdateCompanyUseCase
from ...application.use_cases.delete_company_use_case import DeleteCompanyUseCase

from ...application.dtos.create_company_dto import CreateCompanyDTO
from ...application.dtos.company_response import CompanyResponseDTO
from ...application.dtos.update_company_dto import UpdateCompanyDTO

from shared.responses import SuccessResponse
from shared.exceptions import BusinessException, NotFoundException

class CompanyController: 
    def __init__(
        self, 
        create_company_use_case: CreateCompanyUseCase,
        get_company_by_id_use_case: GetCompanyByIdUseCase, 
        update_company_use_case: UpdateCompanyUseCase,
        delete_company_use_case: DeleteCompanyUseCase
    ): 
        self.create_company_use_case = create_company_use_case
        self.get_company_by_id_use_case = get_company_by_id_use_case
        self.update_company_use_case = update_company_use_case
        self.delete_company_use_case = delete_company_use_case
        
        
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

    async def get_company_id(self, company_id: str) -> SuccessResponse: 
        
        try: 
            company = await self.get_company_by_id_use_case.execute(company_id)
            
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
                message="Company retrieved successfully", 
                status_code=status.HTTP_200_OK
            )
            
        except NotFoundException as e: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=str(e)
            )
        except Exception as e: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Internal Server Error: {str(e)}"
            )

    async def update_company(self, company_id: str, company_dto: UpdateCompanyDTO) -> SuccessResponse: 
        
        try: 
            company = await self.update_company_use_case.execute(company_id, company_dto)
            print(company)

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
                message="Company updated successfully", 
                status_code=status.HTTP_200_OK
            )
        except NotFoundException as e: 
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=str(e)
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

    async def delete_company(self, company_id: str) -> bool: 
        
        try: 
            await self.delete_company_use_case.execute(company_id)

            return SuccessResponse(
                data={"deleted_company_id" : company_id}, 
                message="Company deleted successfully", 
                status_code=status.HTTP_200_OK
            )
        
        except NotFoundException as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail=str(e)
            )
        except Exception as e: 
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
                detail=f"Internal Server Error: {str(e)}"
            ) 
    
    