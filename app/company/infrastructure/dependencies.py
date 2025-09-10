from functools import lru_cache
from config.database import get_database 
from ..domain.repositories.company_repository import CompanyRepository 
from ..infrastructure.repositories.mongodb_company_repository import MongoDBCompanyRepository

from ..application.use_cases.create_company_use_case import CreateCompanyUseCase 

from .controllers.company_controller import CompanyController

@lru_cache()
def get_company_repository() -> CompanyRepository: 
    database = get_database()
    return MongoDBCompanyRepository(database)

@lru_cache()
def get_create_company_use_case() -> CreateCompanyUseCase: 
    company_repository = get_company_repository()
    return CreateCompanyUseCase(company_repository)

@lru_cache() 
def get_company_controller() -> CompanyController: 
    get_company_use_case = get_create_company_use_case() 
    
    return CompanyController(
        create_company_use_case=get_company_use_case
    )