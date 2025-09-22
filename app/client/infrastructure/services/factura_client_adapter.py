import httpx
from typing import Dict, Any
from config.settings import settings
import json
import logging
from ...domain.repositories.external_client_repository import ExternalClientRepository

logger = logging.getLogger(__name__)

class FacturaClientAdapter(ExternalClientRepository):  
    
    def __init__(self):
        self.api_key = settings.factura_com_api_key
        self.secret_key = settings.factura_com_secret_key
        self.base_url = settings.factura_com_api_url
        self.plugin_key = "9d4095c8f7ed5785cb14c0e3b033eeb8252416ed"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def create_client(self, client_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            headers = {
                "F-API-KEY": self.api_key,
                "F-SECRET-KEY": self.secret_key,
                "F-PLUGIN": self.plugin_key
            }
            
            data = {}
            for key, value in client_data.items():
                data[key] = str(value) if value is not None else ''
            
            logger.info(f"Enviando datos de cliente a Factura.com: {json.dumps({k: v for k, v in data.items()}, indent=2)}")
            
            base_url_without_v4 = self.base_url.replace('/v4', '')
            response = await self.client.post(
                f"{base_url_without_v4}/v1/clients/create",
                data=data,  
                headers=headers
            )
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"Respuesta de Factura.com: {json.dumps(result, indent=2)}")
            return result
                
        except httpx.HTTPError as e:
            error_msg = f"Error calling Factura.com API: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f" - Response: {e.response.text}"
                logger.error(f"Status code: {e.response.status_code}")
            logger.error(error_msg)
            raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"ERROR inesperado: {str(e)}", exc_info=True)
            raise Exception(f"Unexpected error: {str(e)}")

    async def get_client_by_id(self, uid: str) -> Dict[str, Any]:
        try:
            headers = {
                "F-API-KEY": self.api_key,
                "F-SECRET-KEY": self.secret_key,
                "F-PLUGIN": self.plugin_key
            }
            
            base_url_without_v4 = self.base_url.replace('/v4', '')
            response = await self.client.get(
                f"{base_url_without_v4}/v1/clients/{uid}",
                headers=headers
            )
            
            response.raise_for_status()
            result = response.json()
            logger.info(f"Datos del cliente obtenidos: {json.dumps(result, indent=2)}")
            return result
            
        except httpx.HTTPError as e:
            error_msg = f"Error obteniendo cliente: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f" - Response: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def close(self):
        await self.client.aclose()