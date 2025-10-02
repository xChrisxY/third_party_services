from typing import List, Optional, Dict, Union, Any
from bson import ObjectId 
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase 

from ...domain.entities.company import Company 
from ...domain.repositories.company_repository import CompanyRepository

from shared.exceptions import BusinessException

class MongoDBCompanyRepository(CompanyRepository): 
    
    def __init__(self, database: AsyncIOMotorDatabase): 
        self.database = database 
        self.collection = database.company

    async def create(self, company: Union[Company, Dict[str, Any]]) -> Company: 
        if isinstance(company, dict):
            company_dict = company.copy()
        elif hasattr(company, 'model_dump'):
            company_dict = company.model_dump(by_alias=True, exclude={"id"})
        elif hasattr(company, 'dict'):
            company_dict = company.dict(by_alias=True, exclude={"id"})
        else:
            raise TypeError(f"company debe ser Company o dict, recibido: {type(company)}")
        
        if 'series' in company_dict: 
            for serie in company_dict['series']: 
                if 'createdAt' not in serie: 
                    serie['createdAt'] = datetime.now(timezone.utc).isoformat()
                if 'updatedAt' not in serie: 
                    serie['updatedAt'] = datetime.now(timezone.utc).isoformat()
        
        result = await self.collection.insert_one(company_dict)
        created_company = await self.collection.find_one({"_id": result.inserted_id})

        if created_company and "_id" in created_company: 
            created_company["_id"] = str(created_company["_id"])

        return Company(**created_company)

    async def get_by_id(self, company_id) -> Optional[Company]:
        try: 
            object_id = ObjectId(company_id)
            company_doc = await self.collection.find_one({"_id": object_id})
            
            if company_doc: 
                company_doc["_id"] = str(company_doc["_id"])
                return Company(**company_doc)
            
            return None
        except Exception: 
            return None

    async def update(self, company_id: str, update_data: dict) -> Company:

        try: 
            object_id = ObjectId(company_id)
        
            existing_company = await self.collection.find_one({"_id": object_id})
            if not existing_company:
                return None
            
            if 'emails' in update_data and update_data['emails']:
                existing_emails = existing_company.get('emails', {})
                update_data['emails'] = {**existing_emails, **update_data['emails']}
            
            result = await self.collection.update_one(
                {"_id": object_id}, 
                {"$set": update_data}
            )
            
            updated_company = await self.collection.find_one({"_id": object_id})
            if updated_company: 
                updated_company["_id"] = str(updated_company["_id"])
                return Company(**updated_company)
            return None
            
            
        except Exception as e: 
            raise BusinessException(f"Error updating company: {str(e)}")

    async def delete(self, company_id):

        try: 
            object_id = ObjectId(company_id)
            
            result = await self.collection.delete_one({
                "_id" : object_id
            })
            
            return result.deleted_count > 0 
        
        except Exception:
            return False