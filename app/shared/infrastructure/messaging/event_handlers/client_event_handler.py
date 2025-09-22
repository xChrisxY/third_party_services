import logging
from client.application.use_cases.sync_client_with_factura_use_case import SyncClientWithFacturaUseCase
from client.infrastructure.repositories.mongodb_client_repository import MongoDBClientRepository
from client.infrastructure.dependencies import get_external_client_repository
from config.database import get_database

logger = logging.getLogger(__name__)

async def handle_client_created_event(event_data: dict):
    try:
        database = get_database()
        client_repository = MongoDBClientRepository(database)
        external_client_repository = get_external_client_repository()

        use_case = SyncClientWithFacturaUseCase(client_repository, external_client_repository)
        result = await use_case.execute(event_data)
        return result
        
    except Exception as e:
        logger.error(f"Error handling client event: {str(e)}")
        return {"success": False, "error": str(e)}