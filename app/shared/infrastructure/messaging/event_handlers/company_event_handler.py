import logging
from company.application.use_cases.sync_company_with_factura_use_case import SyncCompanyWithFacturaUseCase
from company.infrastructure.repositories.mongodb_company_repository import MongoDBCompanyRepository
from company.infrastructure.dependencies import get_external_company_repository
from config.database import get_database

logger = logging.getLogger(__name__)

async def handle_company_created_event(event_data: dict):
    try:
        database = get_database()
        company_repository = MongoDBCompanyRepository(database)
        external_company_repository = get_external_company_repository()

        use_case = SyncCompanyWithFacturaUseCase(company_repository, external_company_repository)
        result = await use_case.execute(event_data)
        return result
        
    except Exception as e:
        logger.error(f"Error handling company event: {str(e)}")
        return {"success": False, "error": str(e)}