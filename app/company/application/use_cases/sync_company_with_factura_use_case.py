from typing import Dict, Any
from ...domain.repositories.company_repository import CompanyRepository
from ...infrastructure.services.factura_client import FacturaClient
import json
import asyncio
import logging
import datetime

logger = logging.getLogger(__name__)

class SyncCompanyWithFacturaUseCase:
    def __init__(
        self, 
        company_repository: CompanyRepository,
        factura_client: FacturaClient
    ):
        self.company_repository = company_repository
        self.factura_client = factura_client

    async def execute(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            logger.info(f"Datos recibidos del evento: {json.dumps(event_data, indent=2)}")
            
            company_data = self._map_to_factura_format(event_data)
            logger.info(f"Datos mapeados para Factura: {json.dumps(company_data, indent=2)}")
            
            response = await self.factura_client.create_company(company_data)
            
            if response.get('status') == 'create': 
                factura_company_id = response.get('0', {}).get('acco_id')
                factura_uid = response.get('0', {}).get('acco_uid')
                
                logger.info(f"¡ÉXITO! Compañía creada con ID: {factura_company_id}, UID: {factura_uid}")
                
                await asyncio.sleep(2) 
                credentials = await self.factura_client.get_company_credentials(factura_uid)
                
                await self._update_company_with_credentials(
                    event_data.get('company_id'), 
                    factura_company_id,
                    credentials
                )
                
                return {
                    "success": True,
                    "factura_company_id": factura_company_id,
                    "factura_uid": factura_uid,
                    "credentials": credentials,
                    "data": response
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

    async def _update_company_with_credentials(self, company_id: str, factura_id: str, credentials: Dict[str, Any]):
        try:
            update_data = {
                "metadata.factura_com_id": factura_id,
                "metadata.factura_uid": credentials.get('data', {}).get('uid'),
                "metadata.factura_api_key": credentials.get('data', {}).get('api_key'),
                "metadata.factura_secret_key": credentials.get('data', {}).get('secret_key'),
                "metadata.synced_with_factura": True,
                "metadata.sync_date": datetime.now().isoformat()
            }
            
            await self.company_repository.update(company_id, update_data)
            logger.info(f"Empresa actualizada con credenciales de Factura.com")
            
        except Exception as e:
           logger.error(f"Could not update company with Factura.com credentials: {str(e)}")