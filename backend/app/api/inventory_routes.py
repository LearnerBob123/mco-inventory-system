# Inventory endpoints
from fastapi import APIRouter

router = APIRouter(prefix="/inventory")

@router.get("/")
def get_inventory():
    pass

