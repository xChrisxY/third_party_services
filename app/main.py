from fastapi import FastAPI 
from fastapi.middleware.cors import CORSMiddleware 
from contextlib import asynccontextmanager 

from config.settings import settings 
from config.database import connect_to_mongo, close_mongo_connection 

from company.infrastructure.routers.company_router import router as company_router 
from client.infrastructure.routers.client_router import router as client_router
from shared.infrastructure.routers.catalog_router import router as catalog_router

@asynccontextmanager 
async def lifespan(app: FastAPI): 
    
    await connect_to_mongo()
    yield
    await close_mongo_connection()

app = FastAPI(
    title=settings.app_name, 
    description="Microservicio de servicio de terceros para soluciones Cloudteen", 
    version=settings.version, 
    debug=settings.debug, 
    lifespan=lifespan, 
    docs_url="/docs", 
    redoc_url="/redoc", 
    openapi_url="/openapi.json"
)

app.add_middleware(
    CORSMiddleware, 
    allow_origins=settings.allowed_origins, 
    allow_credentials=True, 
    allow_methods=["GET", "POST", "PUT", "PATCH", "DELETE"], 
    allow_headers=["*"]
)

@app.get("/", tags=["health"])
async def health_check(): 
    return {
        "status" : "healthy", 
        "service" : settings.app_name, 
        "version" : settings.version
    }

app.include_router(company_router) 
app.include_router(client_router)
app.include_router(catalog_router)

