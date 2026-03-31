
from app.api import inventory_routes  # <--- new import
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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
from app.api import component_v2_routes
from app.api import hierarchy_v2_routes
from app.api import inventory_v2_routes

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create database tables
Base.metadata.create_all(bind=engine)

# Register routers
app.include_router(auth_routes.router)
app.include_router(component_routes.router)
app.include_router(component_v2_routes.router)
app.include_router(hierarchy_v2_routes.router)
app.include_router(inventory_v2_routes.router)
app.include_router(dashboard_routes.router)
app.include_router(inventory_routes.router)
app.include_router(lifecycle_routes.router)
app.include_router(reporting_routes.router)


@app.get("/")
def root():
    return {"message": "MCO Inventory System API Running"}










