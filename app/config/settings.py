from pydantic_settings import BaseSettings 
from typing import Optional 

class Settings(BaseSettings): 
    
    app_name: str = "Third Party Services"
    debug: bool = False 
    version: str = "1.0.0"

    mongo_host: str = "third_party_mongo"
    mongo_user: str = "admin"
    mongo_port: str = "27017"
    mongo_pass: str = "secret123"
    mongo_url: str = f"mongodb://{mongo_user}:{mongo_pass}@{mongo_host}:{mongo_port}"
    database_name: str = "third_party_services_db"

    allowed_origins: list = ["http://localhost:8000"]

    class Config: 
        env_file = ".env"
        
settings = Settings()