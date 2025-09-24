from motor.motor_asyncio import AsyncIOMotorDatabase 

from ...domain.entities.client import Client 
from ...domain.repositories.client_repository import ClientRepository

from shared.exceptions import BusinessException 

class MongoDBClientRepository(ClientRepository): 
    
    def __init__(self, database: AsyncIOMotorDatabase): 
        self.database = database 
        self.collection = database["clients"]
        
    async def create(self, client: Client) -> Client:

        client_dict = client.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(client_dict)
        created_client = await self.collection.find_one({"_id": result.inserted_id})

        if created_client and "_id" in created_client: 
            created_client["_id"] = str(created_client["_id"])

        return Client(**created_client)

    async def get_by_id(self, client_id):
        return await super().get_by_id(client_id)

    async def find_by_rfc(self, client_rfc):
        try:
            client_doc = await self.collection.find_one({"rfc": client_rfc})

            if client_doc: 
                client_doc["_id"] = str(client_doc["_id"])
                return Client(**client_doc)
            
            return None
        except Exception: 
            return None