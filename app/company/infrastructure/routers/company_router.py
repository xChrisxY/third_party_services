from fastapi import APIRouter, Depends, status 

from ..controllers.company_controller import CompanyController 
from ...application.dtos.create_company_dto import CreateCompanyDTO 
from ...application.dtos.company_response import CompanyResponseDTO 

from ..dependencies import get_company_controller 

from shared.responses import SuccessResponse 

router = APIRouter(prefix="/api/v1/invoicing/companies", tags=["companies"])

@router.post(
    "/", 
    response_model=SuccessResponse[CompanyResponseDTO], 
    status_code=status.HTTP_201_CREATED, 
    summary="Create company", 
    description="Create a new company"
)
async def create_company(company_dto: CreateCompanyDTO, controller: CompanyController = Depends(get_company_controller)):
    return await controller.create_company(company_dto)