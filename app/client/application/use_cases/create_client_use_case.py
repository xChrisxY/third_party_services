from ...domain.entities.client import Client
from ...domain.repositories.client_repository import ClientRepository 
from ..dtos.create_client_dto import CreateClientDTO

from shared.exceptions import BusinessException

class CreateClientUseCase:
    
    def __init__(self, client_repository: ClientRepository): 
        self.client_repository = client_repository 
        
    async def execute(self, client_dto: CreateClientDTO) -> Client: 
        
        try: 
            
            client = Client(
                id=client_dto.id, 
                tenant_id=client_dto.tenant_id, 
                external_uid=client_dto.external_uid,
                rfc=client_dto.rfc,
                business_name=client_dto.business_name, 
                tax_regime=client_dto.tax_regime, 
                tax_id_number=client_dto.tax_id_number,
                address=client_dto.address, 
                contact=client_dto.contact, 
                cfdi_use=client_dto.cfdi_use, 
                cfdi_use_name=client_dto.cfdi_use_name, 
                created_at=client_dto.created_at, 
                updated_at=client_dto.updated_at, 
                status=client_dto.status, 
                factura_sync=client_dto.factura_sync
            )

            created_client = await self.client_repository.create(client)
            return created_client
            
        except Exception as e:
            raise BusinessException(f"Failed to create client: {str(e)}")