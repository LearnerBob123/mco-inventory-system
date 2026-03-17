
from app.api import inventory_routes  # <--- new import
from fastapi import FastAPI
from app.api import reporting_routes
from app.api import lifecycle_routes
from app.api import auth_routes, dashboard_routes
from app.database.base import Base
from app.database.session import engine

Base.metadata.create_all(bind=engine)
from app.models.models import Base

# Import API routers
from app.api import auth_routes
from app.api import component_routes

app = FastAPI()

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(auth_routes.router)
app.include_router(component_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(inventory_routes.router)
app.include_router(lifecycle_routes.router)
app.include_router(reporting_routes.router)


@app.get("/")
def root():
    return {"message": "MCO Inventory System API Running"}










