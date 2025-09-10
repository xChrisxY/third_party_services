from typing import List, Optional 
from bson import ObjectId 
from motor.motor_asyncio import AsyncIOMotorDatabase 

from ...domain.entities.company import Company 
from ...domain.repositories.company_repository import CompanyRepository

class MongoDBCompanyRepository(CompanyRepository): 
    
    def __init__(self, database: AsyncIOMotorDatabase): 
        self.database = database 
        self.collection = database.company

    async def create(self, company: Company) -> Company: 
        
        company_dict = company.model_dump(by_alias=True, exclude={"id"})
        result = await self.collection.insert_one(company_dict)
        created_company = await self.collection.find_one({"_id": result.inserted_id})

        if created_company and "_id" in created_company: 
            created_company["_id"] = str(created_company["_id"])

        return Company(**created_company)

    async def get_by_id(self, company_id):
        return await super().get_by_id(company_id)

    async def update(self, company):
        return await super().update(company)

    async def delete(self, company_id):
        return await super().delete(company_id)