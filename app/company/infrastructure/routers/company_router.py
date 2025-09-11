from fastapi import APIRouter, Depends, status 

from ..controllers.company_controller import CompanyController 
from ...application.dtos.create_company_dto import CreateCompanyDTO 
from ...application.dtos.company_response import CompanyResponseDTO 
from ...application.dtos.update_company_dto import UpdateCompanyDTO

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

@router.get(
    "/{company_id}", 
    response_model=SuccessResponse[CompanyResponseDTO], 
    status_code=status.HTTP_200_OK, 
    summary="Get company by id", 
    description="Can retrieve any companie by id"
)
async def get_company_by_id(company_id: str, controller: CompanyController = Depends(get_company_controller)): 
    return await controller.get_company_id(company_id)

@router.put(
    "/{company_id}", 
    response_model=SuccessResponse[CompanyResponseDTO],
    summary="Update company", 
    description="Update a specific company by id"
)
async def update_company(company_id: str, company: UpdateCompanyDTO, controller: CompanyController = Depends(get_company_controller)): 
    return await controller.update_company(company_id, company)

@router.delete(
    "/{company_id}", 
    response_model=SuccessResponse, 
    status_code=status.HTTP_200_OK, 
    summary="Delete Company", 
    description="Delete a specific company"
)
async def delete_company(company_id: str, controller: CompanyController = Depends(get_company_controller)):
    return await controller.delete_company(company_id)

