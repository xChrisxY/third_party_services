import httpx
from typing import Dict, Any, List
from config.settings import settings
import json
import base64
import logging 

logger = logging.getLogger(__name__)

class FacturaClient:
    def __init__(self):
        self.api_key = settings.factura_com_api_key
        self.secret_key = settings.factura_com_secret_key
        self.base_url = settings.factura_com_api_url
        self.plugin_key = "9d4095c8f7ed5785cb14c0e3b033eeb8252416ed"
        self.client = httpx.AsyncClient(timeout=30.0)

    async def create_company(self, form_data: Dict[str, Any]) -> Dict[str, Any]:
        try:
            headers = {
                "F-API-KEY": self.api_key,
                "F-SECRET-KEY": self.secret_key,
                "F-PLUGIN": self.plugin_key
            }
            
            data = {}
            
            for key, value in form_data.items():
                data[key] = str(value) if value is not None else ''
            
            logger.info(f"Enviando datos a Factura.com: {json.dumps({k: v[:100] + '...' if k.endswith('_b64') and v and len(v) > 100 else v for k, v in data.items()}, indent=2)}")
            
            response = await self.client.post(
                f"{self.base_url}/account/create",
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
            logger.error(error_msg)
            raise Exception(error_msg)
                
        except Exception as e:
            logger.error(f"ERROR inesperado: {str(e)}")
            raise Exception(f"Unexpected error: {str(e)}")

    async def get_company_credentials(self, uid: str) -> Dict[str, Any]:
        try:
            logger.info(f"Obteniendo credenciales reales para UID: {uid}")
            
            headers = {
                "F-API-KEY": self.api_key,
                "F-SECRET-KEY": self.secret_key,
                "F-PLUGIN": self.plugin_key,
                "Content-Type": "application/json"
            }
            
            base_url_without_v4 = self.base_url.replace('/v4', '')
            url = f"{base_url_without_v4}/v1/account/{uid}"
            
            logger.info(f"URL de credenciales: {url}")
            logger.info(f"Headers: { {k: v for k, v in headers.items() if k != 'F-SECRET-KEY'} }")
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            result = response.json()
            logger.info(f"Credenciales obtenidas: {result.get('status')}")
            
            return result
            
        except httpx.HTTPError as e:
            error_msg = f"Error obteniendo credenciales: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f" - Response: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def close(self):
        await self.client.aclose()