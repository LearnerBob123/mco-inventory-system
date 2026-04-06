from fastapi import APIRouter

from app.api.routes.components import router as component_router
from app.api.routes.guns import router as gun_router
from app.api.routes.inventory import router as inventory_router
from app.api.routes.users import router as user_router
from app.api.routes.workflows import router as workflow_router
from app.api.routes.work_orders import router as work_order_router


api_router = APIRouter()
api_router.include_router(component_router)
api_router.include_router(gun_router)
api_router.include_router(inventory_router)
api_router.include_router(user_router)
api_router.include_router(workflow_router)
api_router.include_router(work_order_router)


