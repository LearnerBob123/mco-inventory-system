from fastapi import FastAPI
from app.core.database import engine
from app.models.models import Base

# Import API routers
from app.api import auth_routes
from app.api import component_routes
from app.services.module_g.routers import router as audit_router

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(auth_routes.router)
app.include_router(component_routes.router)
app.include_router(audit_router)

@app.get("/")
def root():
    return {"message": "MCO Inventory System API Running"}