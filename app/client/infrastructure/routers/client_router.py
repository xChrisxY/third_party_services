from fastapi import APIRouter, Depends, status 

from ..controllers.client_controller import ClientController 
from ...application.dtos.create_client_dto import CreateClientDTO 
from ...application.dtos.client_response import ClientResponseDTO 

from ..dependencies import get_client_controller 
from shared.responses import SuccessResponse 

router = APIRouter(prefix="/api/v1/invoicing/clients", tags=["clients"])

@router.post(
    "/", 
    response_model=SuccessResponse[ClientResponseDTO], 
    status_code=status.HTTP_201_CREATED, 
    summary="Create Client", 
    description="Create a new client"
)
async def create_client(client_dto: CreateClientDTO, controller: ClientController = Depends(get_client_controller)):
    return await controller.create_client(client_dto)