from fastapi import APIRouter, HTTPException, Query, status
from typing import List, Dict, Any, Optional 
import logging 
from ..services.factura_catalog_service import FacturaCatalogService 
from ..dependencies import get_factura_catalog_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/catalogs", tags=["catalogs"])

catalog_service = get_factura_catalog_service()

@router.get("/cfdi-uses")
async def get_cfdi_uses(
    regime_code: Optional[str] = Query(None, description="Filtrar por régimen fiscal compatible")
) -> Dict[str, Any]: 
    try: 
        
        cfdi_uses = await catalog_service.get_cfdi_uses()
        
        if regime_code:
            filtered_uses = []
            for cfdi in cfdi_uses:
                if regime_code in cfdi.get('regimenes', []): 
                    filtered_uses.append(cfdi)
            return {"success": True, "data": cfdi_uses}
        
        return {"success": True, "data": cfdi_uses}
        
    except Exception as e: 
        logger.error(f"Error obteniendo CFDI uses: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

        
@router.get("/tax-regimes")
async def get_tax_regimes(
    person_type: Optional[str] = Query(None, description="Tipo de persona: fisca|moral")
) -> Dict[str, Any]:
    
    try: 
        
        regimes = await catalog_service.get_tax_regimes()
        
        if person_type:
            filtered_regimes = []
            for regime in regimes: 
                if person_type == "fisica" and regime.get('fisica'):
                    filtered_regimes.append(regime)
                if person_type == "moral" and regime.get('moral'):
                    filtered_regimes.append(regime)
                return {"success": True, "data": filtered_regimes}
        
        return {"success": True, "data": regimes}
        
    except Exception as e: 
        logger.error(f"Error obteniendo tax regimes: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")

@router.get('/countries')
async def get_countries() -> Dict[str, Any]: 
    try:
        countries = await catalog_service.get_countries()
        return {"success": True, "data": countries}
    except Exception as e:
        logger.error(f"Error obteniendo countries: {str(e)}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error interno del servidor")