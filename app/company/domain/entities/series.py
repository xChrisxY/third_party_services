from pydantic import BaseModel, Field 
from typing import Optional 
from datetime import datetime, timezone

class Series(BaseModel): 
    serie_id: str = Field(..., alias="serieId", description="ID único de la serie")
    name: str = Field(..., description="Nombre de la serie")
    type: str = Field(..., description="Tipo de la serie")
    description: str = Field(..., description="Descripción de la serie")
    status: str = Field(..., description="Estado de la serie")
    branch_id: Optional[str] = Field(None, alias="branchId", description="ID de la sucursal")
    folio: int = Field(default=1, description="Último folio utilizado")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="createdAt")
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), alias="updatedAt")

    class Config:
        populate_by_name = True
        extra = "allow"