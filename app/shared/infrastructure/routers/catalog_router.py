from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any, Optional 
import logging 
from ..services.factura_catalog_service import FacturaCatalogService 
from ..dependencies import get_factura_catalog_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="api/catalogs", tags=["catalogs"])

catalog_service = get_factura_catalog_service()

@router.get("/cfdi-uses")
async def get_cfdi_uses(
    regime_code: Optional[str] = Query(None, description="Filtrar por régimen fiscal compatible")
) -> Dict[str, Any]: 
    try: 
        
        cfdi_uses = await catalog_service.get_cfdi_uses()
        
        
    except Exception as e: 
        logger.error(f"Error obteniendo CFDI uses: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")