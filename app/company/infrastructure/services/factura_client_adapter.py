from typing import Dict, Any, Optional, List
import httpx
import json
import logging
import asyncio 

from config.settings import settings
from ...domain.repositories.external_company_repository import ExternalCompanyRepository
from ...domain.entities.series import Series

logger = logging.getLogger(__name__)

class FacturaClientAdapter(ExternalCompanyRepository):  
    
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
            return response.json()
                
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
            
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            
            return response.json()
            
        except httpx.HTTPError as e:
            error_msg = f"Error obteniendo credenciales: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error_msg += f" - Response: {e.response.text}"
            logger.error(error_msg)
            raise Exception(error_msg)

    async def get_all_series(self) -> List[Dict[str, Any]]:
        try: 
            headers = {
                "F-API-KEY": self.api_key, 
                "F-SECRET-KEY": self.secret_key, 
                "F-PLUGIN": self.plugin_key
            }

            url = f"{self.base_url}/series"
            logger.info("Obteniendo todas las series")

            response = await self.client.get(
                url=url, 
                headers=headers
            )

            response.raise_for_status()
            
            series_data = response.json()
            logger.info(f"Respuesta de todas las series: {series_data}")

            if series_data.get("status") == "success": 
                return series_data.get("data", [])
            else: 
                logger.warning("No se pudieron obtener las series")

        except httpx.HTTPError as e: 
            msg = f"Error obteniendo series de Factura.com: {str(e)}"
            if hasattr(e, 'response') and e.response: 
                msg += f" - Response: {e.response.text}"
            logger.error(msg)
            raise Exception(msg)
        except Exception as e: 
            logger.error(f"Error inesperado obteniendo series: {str(e)}")
            raise

    async def get_series_by_name(self, series_name: str) -> Optional[Dict[str, Any]]:
        
        try: 
            all_series = await self.get_all_series()
            
            for serie in all_series: 
                if serie.get("SerieName") == series_name:
                    logger.info(f"Serie encontrada por nombre '{series_name}': {serie}")
                    return serie 
                
            logger.warning(f"No se encontró serie con nombre '{series_name}'")
            return None
            
        except Exception as e: 
            logger.error(f"Error buscando serie por nombre: {str(e)}")
            raise

    async def get_default_series(self, company_uid: str) -> Optional[Dict[str, Any]]:
        
        try: 
            
            all_series = await self.get_all_series()           

            for serie in all_series:
                if serie.get("SerieType") == "factura":
                    logger.info(f"Serie por defecto encontrada: {serie}")
                    return Series(
                        serie_id = str(serie.get("SerieID")),
                        name = serie.get("SerieName"),
                        type = serie.get("SerieType"),
                        description =  serie.get("SerieDescription"),
                        status = serie.get("SerieStatus"),
                        branch_id = None
                    )

            logger.warning("No se encontró serie de tipo 'factura' en las series por defecto")
            return None
        
        except  httpx.HTTPError as e: 
            error = f"Error obteniendo series de Factura.com: {str(e)}"
            if hasattr(e, 'response') and e.response:
                error += f" - Response: {e.response.text}"
            logger.error(error)
            raise Exception(error)
            
        except Exception as e: 
            logger.error(f"Error inesperado obteniendo series: {str(e)}")
            raise

    async def create_series(self, company_uid: str, series_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        try:
            
            headers = {
                "F-API-KEY": self.api_key, 
                "F-SECRET-KEY": self.secret_key, 
                "F-PLUGIN": self.plugin_key, 
                "Content-Type": "application/json"
            }

            created_series = []
            for serie in series_data:
                payload = {
                    "letra": serie.get("name"),
                    "tipoDocumento": serie.get("type", "factura"),
                    "folio": serie.get("initial_folio", 1)
                }

                payload = {k: v for k, v in payload.items() if v is not None}

                logger.info(f"Creando serie en Factura.com: {payload}")

                response = await self.client.post(
                    f"{self.base_url}/series/create", 
                    json=payload, 
                    headers=headers
                )
                
                response.raise_for_status()
                
                result = response.json()
                logger.info(f"Respuesta de creación de serie: {result}")

                if result.get("response") == "success": 
                    
                    await asyncio.sleep(1)

                    series_name = serie.get("name")
                    serie_info = await self.get_series_by_name(series_name)
                    
                    if serie_info: 
                        created_series.append({
                            "serie_id": str(serie_info.get("SerieID")),
                            "name": serie_info.get("SerieName"),
                            "type": serie_info.get("SerieType"),
                            "description": serie_info.get("SerieDescription", ""),
                            "status": serie_info.get("SerieStatus", "Activa"),
                            "branch_id": serie.get("branch_id"),
                            "folio": serie.get("initial_folio", 1),
                        }) 
                    else: 
                        logger.error(f"No se pudo obtener la información completa de la serie")
                        created_series.append({
                            "serie_id": "unknown",
                            "name": series_name,
                            "type": serie.get("type", "factura"),
                            "description": serie.get("description", f"Serie {series_name}"),
                            "status": "Activa",
                            "branch_id": serie.get("branch_id"),
                            "folio": serie.get("initial_folio", 1)
                        })
                    
                else: 
                    error_msg = result.get('message', 'Unknown error from Factura.com')
                    logger.error(f"Error creando la serie: {error_msg}") 
                    raise Exception(f"Error creando serie: {error_msg}")

                return created_series
            
        except Exception as e:
            logger.error(f"Error creando series: {str(e)}")
            raise
        

    async def close(self):
        await self.client.aclose()