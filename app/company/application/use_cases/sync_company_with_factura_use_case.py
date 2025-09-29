from typing import Dict, Any, List
from ...domain.entities.company import Company
from ...domain.repositories.company_repository import CompanyRepository
from ...domain.repositories.external_company_repository import ExternalCompanyRepository
from ...domain.repositories.credential_repository import CredentialRepository
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
            
            company_data = self._map_to_factura_format(event_data)
            logger.info(f"Datos mapeados para Factura: {json.dumps(company_data, indent=2)}")

            series_to_create = event_data.get("series", [])
            has_new_series = len(series_to_create) > 0
            
            response = await self.external_company_repository.create_company(company_data)
            
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
                    event_data, 
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

    def _map_to_factura_format(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        fiscal_data = event_data.get("fiscal_data", {})
        contact = event_data.get("contact", {})
        emails = event_data.get("emails", {})
        certificates = event_data.get("certificates", {})
        smtp_config = event_data.get("smtp_config", {})
        
        form_data = {
            "razons": event_data.get("business_name"),
            "rfc": fiscal_data.get("tax_id"),
            "codpos": fiscal_data.get("zip_code"),
            "calle": fiscal_data.get("street"),
            "numero_exterior": fiscal_data.get("ext_number"),
            "numero_interior": fiscal_data.get("int_number"),
            "colonia": fiscal_data.get("neighborhood"),
            "estado": fiscal_data.get("state"),
            "ciudad": fiscal_data.get("city"),
            "delegacion": fiscal_data.get("municipality", ""),
            "email": emails.get("contact"),
            "regimen": fiscal_data.get("tax_regime"),
            "mailtomyconta": "1" if emails.get("accounting") else "0",
            "mail_conta": emails.get("accounting", ""),
            "mailtomyself": "1",
            "telefono": contact.get("phone"),
            "curp": fiscal_data.get("curp", ""),
            "password": certificates.get("fiel_password", "12345678a"),
        }
        
        if certificates.get('fiel_cer'):
            form_data["fiel_cer_b64"] = certificates['fiel_cer']
        if certificates.get('fiel_key'):
            form_data["fiel_key_b64"] = certificates['fiel_key']
        if certificates.get('csd_cer'):
            form_data["csd_cer_b64"] = certificates['csd_cer']
        if certificates.get('csd_key'):
            form_data["csd_key_b64"] = certificates['csd_key']
        if certificates.get('fiel_password'):
            form_data["fielpassword"] = certificates['fiel_password']
        
        if smtp_config:
            form_data.update({
                "smtp": "1",
                "smtp_email": smtp_config.get("email"),
                "smtp_password": smtp_config.get("password"),
                "smtp_port": smtp_config.get("port"),
                "smtp_host": smtp_config.get("host"),
                "smtp_encryption": smtp_config.get("encryption", "tls"),
            })
        else:
            form_data["smtp"] = "0"
        
        return form_data

    async def _update_company_with_real_credentials(self, company_id: str, real_credentials: Dict[str, Any]):
        try:
            logger.info(f"Credenciales recibidas: {json.dumps(real_credentials, indent=2)}")

            encrypted_credentials = await self.credential_repository.encrypt_credentials(real_credentials)
            
            update_data = {
                "metadata.apiKey": encrypted_credentials.get('api_key'),    
                "metadata.apiSecret": encrypted_credentials.get('secret_key'), 
                "metadata.thpFcUid": real_credentials.get('uid', ''),
                #"metadata.razonSocial": real_credentials.get('razon_social', ''),
                #"metadata.rfc": real_credentials.get('rfc', ''),
                #"metadata.regimenFiscal": real_credentials.get('regimen_fiscal', ''),
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
                
                created_series = await self.external_company_repository.create_series(company_uid, new_series)
                return created_series
            else: 
                logger.info("No hay nuevas series, obteniendo serie por defecto de Factura.com")
                default_series = await self.external_company_repository.get_default_series(company_uid)
                if default_series: 
                    return [default_series]
                else:  
                    logger.warning("No se pudo obtener serie por defecto, retornando lista vacía")
                    return []
        except Exception as e: 
            logger.error(f"Error procesando series: {str(e)}")
            return []

    async def _create_company_in_database(
        self, 
        event_data: Dict[str, Any], 
        factura_id: str, 
        credentials: Dict[str, Any], 
        company_series: List[Dict[str, Any]]
    ) -> str:
        try:
            credentials_data = credentials.get('data', {})

            company_dict = {
                "tenant_id": event_data.get("company_id", str(uuid.uuid4())), 
                "business_name": event_data.get("business_name"),
                "trade_name": event_data.get("trade_name"),
                
                "source": {
                    "service": "external",
                    "serviceId": event_data.get("company_id"),
                    "referralCode": None
                },
                
                "contact": {
                    "name": event_data.get("contact", {}).get("name", ""),
                    "phone": event_data.get("contact", {}).get("phone", ""),
                    "email": event_data.get("emails", {}).get("contact", "")
                },
                
                "fiscal_data": {
                    "legalName": event_data.get("business_name", ""),
                    "taxId": event_data.get("fiscal_data", {}).get("tax_id", ""),
                    "taxRegime": event_data.get("fiscal_data", {}).get("tax_regime", ""),
                    "zipCode": event_data.get("fiscal_data", {}).get("zip_code", ""),
                    "street": event_data.get("fiscal_data", {}).get("street", ""),
                    "extNumber": event_data.get("fiscal_data", {}).get("ext_number", ""),
                    "intNumber": event_data.get("fiscal_data", {}).get("int_number"),
                    "neighborhood": event_data.get("fiscal_data", {}).get("neighborhood", ""),
                    "state": event_data.get("fiscal_data", {}).get("state", ""),
                    "city": event_data.get("fiscal_data", {}).get("city", ""),
                    "country": "México"
                },
                
                "emails": {
                    "contact": event_data.get("emails", {}).get("contact", ""),
                    "owner": event_data.get("emails", {}).get("contact", ""), 
                    "billing": event_data.get("emails", {}).get("contact", ""),
                    "accountant": event_data.get("emails", {}).get("accounting", "")
                },
                
                "configs": {
                    "sendCopyToClient": True,
                    "sendCopyToAccountant": bool(event_data.get("emails", {}).get("accounting")),
                    "notifications": {
                        "whatsapp": False,
                        "slack": False,
                        "webhookUrl": None
                    }
                },
                
                "metadata": {
                    "apiKey": credentials_data.get('api_key'),     
                    "apiSecret": credentials_data.get('secret_key'), 
                    "thpFcUid": credentials_data.get('uid'),  
                    "createdAt": datetime.now().isoformat(),
                    "updatedAt": datetime.now().isoformat(),
                    "status": "active"
                }, 
                
                "series": company_series
            }
            
            company_model = Company(**company_dict)
            created_company = await self.company_repository.create(company_model)
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