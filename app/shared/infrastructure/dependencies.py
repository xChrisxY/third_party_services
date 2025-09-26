from functools import lru_cache
from .services.factura_catalog_service import FacturaCatalogService

@lru_cache()
def get_factura_catalog_service() -> FacturaCatalogService:
    return FacturaCatalogService()