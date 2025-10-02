from typing import Dict, Any, List
from ...domain.entities.company import Company
from ...domain.repositories.company_repository import CompanyRepository
from ...domain.repositories.external_company_repository import ExternalCompanyRepository
from ...domain.repositories.credential_repository import CredentialRepository

from ..dtos.company_event_dto import CompanyEventDTO 
from ..dtos.factura_company_dto import FacturaCompanyDTO 
from ..dtos.company_mongo_dto import CompanyMongoDTO

import json
import asyncio
import logging
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class SyncCompanyWithFacturaUseCase:
    def __init__(
        self, 
        company_repository: CompanyRepository,
        external_company_repository: ExternalCompanyRepository, 
        credential_repository: CredentialRepository

    ):
        self.company_repository = company_repository
        self.external_company_repository = external_company_repository
        self.credential_repository = credential_repository

    async def execute(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Datos recibidos del evento: {json.dumps(event_data, indent=2)}")
            event_dto = CompanyEventDTO(**event_data)
            
            factura_dto = FacturaCompanyDTO.from_event_dto(event_dto)
            logger.info(f"Datos para factura: {factura_dto.model_dump(exclude_none=True)}")

            series_to_create = event_data.get("series", [])
            has_new_series = len(series_to_create) > 0
            
            response = await self.external_company_repository.create_company(factura_dto.model_dump(exclude_none=True))
            
            if response.get('status') == 'create': 
                factura_company_id = response.get('0', {}).get('acco_id')
                factura_uid = response.get('0', {}).get('acco_uid')
                
                logger.info(f"¡ÉXITO! Compañía creada con ID: {factura_company_id}, UID: {factura_uid}")

                company_series = await self._process_series(
                    factura_uid, 
                    has_new_series, 
                    series_to_create
                )
                
                await asyncio.sleep(2) 
                credentials = await self.external_company_repository.get_company_credentials(factura_uid)
                
                company_id = await self._create_company_in_database(
                    event_dto,
                    factura_company_id, 
                    credentials, 
                    company_series
                )

                await asyncio.sleep(3)
                credentials_response = await self.external_company_repository.get_company_credentials(factura_uid)

                if credentials_response.get("status") == "success":
                    await self._update_company_with_real_credentials(
                        str(company_id), 
                        credentials_response.get('data', {})
                    )

                    logger.info(f"Credenciales REALES obtenidas y guardadas para empresa {company_id}")
                
                return {
                    "success": True,
                    "factura_company_id": factura_company_id,
                    "factura_uid": factura_uid,
                    "message": "Company succesfully created in both Factura.com and local database"
                }
            else:
                error_msg = response.get('message', 'Unknown error from Factura.com')
                logger.error(f"Error de Factura.com: {error_msg}")
                return {
                    "success": False,
                    "error": error_msg
                }
                
        except Exception as e:
            logger.error(f"Error inesperado en use case: {str(e)}")
            return {"success": False, "error": str(e)}

    async def _update_company_with_real_credentials(self, company_id: str, real_credentials: Dict[str, Any]):
        try:
            logger.info(f"Credenciales recibidas: {json.dumps(real_credentials, indent=2)}")

            encrypted_credentials = await self.credential_repository.encrypt_credentials(real_credentials)
            
            update_data = {
                "metadata.apiKey": encrypted_credentials.get('api_key'),    
                "metadata.apiSecret": encrypted_credentials.get('secret_key'), 
                "metadata.thpFcUid": real_credentials.get('uid', ''),
                "metadata.razonSocial": real_credentials.get('razon_social', ''),
                "metadata.rfc": real_credentials.get('rfc', ''),
                "metadata.regimenFiscal": real_credentials.get('regimen_fiscal', ''),
                "metadata.updatedAt": datetime.now().isoformat(),
                #"metadata.credentialStatus": "decrypted" 
            }
            
            logger.info(f"Datos de actualización: {json.dumps(update_data, indent=2)}")
            
            await self.company_repository.update(company_id, update_data)
            
                
        except Exception as e:
            logger.error(f"Error actualizando credenciales REALES: {str(e)}")
            raise

    async def _process_series(self, company_uid: str, has_new_series: bool, new_series: List[Dict[str, Any]]): 
        try: 
            if has_new_series: 
                logger.info(f"Creando {len(new_series)} nuevas series en base de datos")
                
                mapped_series = []
                for serie in new_series:
                    mapped_series.append({
                        "name": serie.get("name"),
                        "type": serie.get("type", "factura"),
                        "description": serie.get("description", f"Serie {serie.get('name')}"),
                        "branch_id": serie.get("branch_id"),
                        "initial_folio": serie.get("initial_folio", 1)
                    })
                
                created_series = await self.external_company_repository.create_series(company_uid, mapped_series)
                
                if created_series and isinstance(created_series[0], object) and not isinstance(created_series[0], dict):
                    return [series.model_dump() if hasattr(series, 'model_dump') else series.dict() if hasattr(series, 'dict') else series for series in created_series]
                return created_series
                
            else: 
                logger.info("No hay nuevas series, obteniendo serie por defecto de Factura.com")
                default_series = await self.external_company_repository.get_default_series(company_uid)
                if default_series: 
                    if hasattr(default_series, 'model_dump'):
                        return [default_series.model_dump()]
                    elif hasattr(default_series, 'dict'):
                        return [default_series.dict()]
                    else:
                        return [default_series]
                else:  
                    logger.warning("No se pudo obtener serie por defecto, retornando lista vacía")
                    return []
        except Exception as e: 
            logger.error(f"Error procesando series: {str(e)}")
            return []

    async def _create_company_in_database(
        self, 
        event_dto: CompanyEventDTO,
        factura_id: str, 
        credentials: Dict[str, Any], 
        company_series: List[Dict[str, Any]]
    ) -> str:
        try:

            database_dto = CompanyMongoDTO.from_event_dto(
                event_dto, factura_id, credentials, company_series
            )
            company_dict = database_dto.model_dump(by_alias=True, exclude_none=True)
            
            logger.info(f"Insertando en BD...")
            created_company = await self.company_repository.create(company_dict)
            if hasattr(created_company, 'inserted_id'):
                company_id = str(created_company.inserted_id)
            elif hasattr(created_company, 'id'):
                company_id = str(created_company.id)
            else:
                company_id = str(created_company)
            
            logger.info(f"Empresa creada en BD con ObjectId: {company_id}")
            return company_id
            
        except Exception as e:
            logger.error(f"Error creando empresa en BD: {str(e)}")
            raise