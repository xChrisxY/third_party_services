from functools import lru_cache 
from config.database import get_database 
from ..domain.repositories.client_repository import ClientRepository 
from ..domain.repositories.external_client_repository import ExternalClientRepository
from ..infrastructure.repositories.mongodb_client_repository import MongoDBClientRepository
from .services.factura_client_adapter import FacturaClientAdapter

from ..application.use_cases.create_client_use_case import CreateClientUseCase

from .controllers.client_controller import ClientController

@lru_cache()
def get_client_repository() -> ClientRepository: 
    database = get_database()
    return MongoDBClientRepository(database)

@lru_cache()
def get_external_client_repository() -> ExternalClientRepository:
    return FacturaClientAdapter()

@lru_cache()
def get_create_client_use_case() -> CreateClientUseCase:
    client_repository = get_client_repository()
    return CreateClientUseCase(client_repository)

@lru_cache()
def get_client_controller() -> ClientController: 
    create_client_use_case = get_create_client_use_case()
    
    return ClientController(
        create_client_use_case=create_client_use_case
    )