import httpx 
from typing import Dict, List, Any 
from config.settings import settings 
import logging 
from datetime import datetime, timedelta, timezone

logger = logging.getLogger(__name__)

class FacturaCatalogService:
    
    def __init__(self):
        self.api_key = settings.factura_com_api_key 
        self.secret_key = settings.factura_com_secret_key
        self.base_url = settings.factura_com_api_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self._cache = {}
        self._cache_expiry = {}

    async def get_cfdi_uses(self) -> List[Dict[str, Any]]:
        cache_key = "cfdi_uses"
        if await self._is_cache_valid(cache_key):
            return self._cache[cache_key]

        try: 
            
            headers = {
                "F-API-KEY": self.api_key, 
                "F-SECRET-KEY": self.secret_key
            }

            response = await self.client.get(
                f"{self.base_url}/catalogo/UsoCfdi", 
                headers=headers
            )

            response.raise_for_status()
            
            catalog_data = response.json() 
            self._cache[cache_key] = catalog_data
            self._cache_expiry[cache_key] = datetime.now(timezone.utc) + timedelta(hours=24)

            return catalog_data
             
        except Exception as e: 
            logger.error(f"Error obteniendo catálogo CFDI: {str(e)}")
            return []

            
    async def get_tax_regimes(self) -> List[Dict[str, Any]]: 
        cache_key = "tax_regimes" 
        if await self._is_cache_valid(cache_key): 
            return self._cache[cache_key]
        
        try: 
            
            headers = {
                "F-API-KEY": self.api_key, 
                "F-SECRET-KEY": self.secret_key
            }
            
            base_url = self.base_url.replace('/v4', '')
            response = await self.client.get(
                f"{base_url}/v3/catalogo/RegimenFiscal", 
                headers=headers
            )

            response.raise_for_status()
            
            regimes_data = response.json()
            self._cache[cache_key] = regimes_data
            self._cache_expiry[cache_key] = datetime.now(timezone.utc) + timedelta(hours=24)

            return regimes_data
             
        except Exception as e: 
            logger.error(f"Error obteniendo catálogo de regímenes: {str(e)}")
            
    
    async def get_countries(self) -> List[Dict[str, Any]]: 
        cache_key = "countries"
        if await self._is_cache_valid(cache_key):
            return self._cache[cache_key]
        
        try: 
            
            headers = {
                "F-API-KEY" : self.api_key, 
                "F-SECRET-KEY" : self.secret_key
            }
            
            base_url = self.base_url.replace('/v4', '')
            response = await self.client.get(
                f"{base_url}/v3/catalogo/Pais", 
                headers=headers
            )
            
            response.raise_for_status() 
            
            countries_data = response.json()
            self._cache[cache_key] = countries_data
            self._cache_expiry[cache_key] = datetime.now(timezone.utc) + timedelta(hours=24)

            return countries_data
            
        except Exception as e: 
            logger.error(f"Error obteniendo catálogo países: {str(e)}")
            return []

    async def validate_cfdi_use(self, cfdi_use: str, tax_regime: str = None) -> Dict[str, Any]:
        cfdi_uses = await self.get_cfdi_uses()
        
        for cfdi in cfdi_uses:
            if cfdi.get('key') == cfdi_use:
                if tax_regime and tax_regime not in cfdi.get('regimenes', []):
                    return {
                        "valid": False,
                        "error": f"El uso CFDI {cfdi_use} no es compatible con el régimen {tax_regime}",
                        "compatible_regimes": cfdi.get('regimenes', [])
                    }
                return {
                    "valid": True,
                    "name": cfdi.get('name'),
                    "use": cfdi.get('use')
                }
        
        return {"valid": False, "error": f"Uso CFDI no válido: {cfdi_use}"}

    async def validate_tax_regime(self, regime_code: str) -> Dict[str, Any]:
        regimes = await self.get_tax_regimes()
        
        for regime in regimes:
            if regime.get('key') == regime_code:
                return {
                    "valid": True,
                    "name": regime.get('name'),
                    "physical_person": regime.get('fisica', False),
                    "moral_person": regime.get('moral', False)
                }
        
        return {"valid": False, "error": f"Régimen fiscal no válido: {regime_code}"}

    async def validate_country(self, country_code: str) -> bool:
        countries = await self.get_countries()
        country_codes = [country.get('key') for country in countries]
        return country_code in country_codes 

    async def _is_cache_valid(self, cache_key: str) -> bool: 
        if cache_key not in self._cache: 
            return False 
        if cache_key not in self._cache_expiry: 
            return False 
        return datetime.now(timezone.utc) < self._cache_expiry[cache_key]