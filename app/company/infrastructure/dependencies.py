from functools import lru_cache
from config.database import get_database 
from ..domain.repositories.company_repository import CompanyRepository 
from ..infrastructure.repositories.mongodb_company_repository import MongoDBCompanyRepository

from ..application.use_cases.create_company_use_case import CreateCompanyUseCase 
from ..application.use_cases.get_company_by_id_use_case import GetCompanyByIdUseCase
from ..application.use_cases.update_company_use_case import UpdateCompanyUseCase
from ..application.use_cases.delete_company_use_case import DeleteCompanyUseCase

from .controllers.company_controller import CompanyController

from .services.factura_client_adapter import FacturaClientAdapter
from ..domain.repositories.external_company_repository import ExternalCompanyRepository
from ..application.use_cases.sync_company_with_factura_use_case import SyncCompanyWithFacturaUseCase


@lru_cache()
def get_sync_company_use_case() -> SyncCompanyWithFacturaUseCase:
    company_repository = get_company_repository()
    external_company_repository = get_external_company_repository()
    return SyncCompanyWithFacturaUseCase(company_repository, external_company_repository)

@lru_cache()
def get_company_repository() -> CompanyRepository: 
    database = get_database()
    return MongoDBCompanyRepository(database)

@lru_cache()
def get_create_company_use_case() -> CreateCompanyUseCase: 
    company_repository = get_company_repository()
    return CreateCompanyUseCase(company_repository)

@lru_cache()
def get_get_company_by_id_use_case() -> GetCompanyByIdUseCase: 
    company_repository = get_company_repository()
    return GetCompanyByIdUseCase(company_repository)

@lru_cache()
def get_update_company_use_case() -> UpdateCompanyUseCase: 
    company_repository = get_company_repository()
    return UpdateCompanyUseCase(company_repository)

@lru_cache()
def get_delete_company_use_case() -> DeleteCompanyUseCase: 
    company_repository = get_company_repository()
    return DeleteCompanyUseCase(company_repository)

@lru_cache()
def get_external_company_repository() -> ExternalCompanyRepository:
    return FacturaClientAdapter()

@lru_cache() 
def get_company_controller() -> CompanyController: 
    create_company_use_case = get_create_company_use_case()
    get_company_use_case = get_get_company_by_id_use_case()
    update_company_use_case = get_update_company_use_case()
    delete_company_use_case = get_delete_company_use_case()
    
    return CompanyController(
        create_company_use_case=create_company_use_case, 
        get_company_by_id_use_case=get_company_use_case, 
        update_company_use_case=update_company_use_case,
        delete_company_use_case = delete_company_use_case
    )