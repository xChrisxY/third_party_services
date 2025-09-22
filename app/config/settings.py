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

    rabbitmq_host: str = "rabbitmq"
    rabbitmq_port: int = 5672 
    rabbitmq_username: str = "guest"
    rabbitmq_password: str = "guest"
    rabbitmq_vhost: str = "/"
    
    company_created_queue: str = "company_created"
    company_created_routing_key: str = "company_created"

    client_created_queue: str = "client_created"
    client_created_routing_key: str = "client_created"
    
    factura_com_api_key: str
    factura_com_secret_key: str
    factura_com_api_url: str = "https://sandbox.factura.com/api/v4"

    allowed_origins: list = ["http://localhost:8000"]

    class Config: 
        env_file = ".env"
        
settings = Settings()