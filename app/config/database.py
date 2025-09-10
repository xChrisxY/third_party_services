from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase 
from typing import Optional 
from .settings import settings

class DatabaseConnection: 
    client: Optional[AsyncIOMotorClient] = None 
    database: Optional[AsyncIOMotorDatabase] = None 
    
db_connection = DatabaseConnection()

async def connect_to_mongo():
    db_connection.client = AsyncIOMotorClient(settings.mongo_url)
    db_connection.database = db_connection.client[settings.database_name]

async def close_mongo_connection(): 
    if db_connection.client: 
        db_connection.client.close()

def get_database() -> Optional[AsyncIOMotorDatabase]: 
    return db_connection.database

