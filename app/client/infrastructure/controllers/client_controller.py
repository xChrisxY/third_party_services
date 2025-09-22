from fastapi import HTTPException, status 

from ...application.use_cases.create_client_use_case import CreateClientUseCase

from ...application.dtos.client_response import ClientResponseDTO 
from ...application.dtos.create_client_dto import CreateClientDTO 

from shared.responses import SuccessResponse 
from shared.exceptions import BusinessException, NotFoundException 

class ClientController:
    
    def __init__(self, create_client_use_case: CreateClientUseCase): 
        self.create_client_use_case = create_client_use_case
        
    async def create_client(self, client_dto: CreateClientDTO) -> SuccessResponse: 
        
        try: 
            
            client = await self.create_client_use_case.execute(client_dto)
            
            client_response = ClientResponseDTO(
                id=client.id, 
                tenant_id=client.tenant_id, 
                external_uid=client.external_uid,
                rfc=client.rfc,
                business_name=client.business_name, 
                tax_regime=client.tax_regime, 
                tax_id_number=client.tax_id_number,
                address=client.address, 
                contact=client.contact, 
                cfdi_use=client.cfdi_use, 
                cfdi_use_name=client.cfdi_use_name, 
                created_at=client.created_at, 
                updated_at=client.updated_at, 
                status=client.status, 
                factura_sync=client.factura_sync
            )
             
            return SuccessResponse(
                data=client_response, 
                message="Client created successfully", 
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

    async def get_by_id(self, client_id: str) -> SuccessResponse:
        pass