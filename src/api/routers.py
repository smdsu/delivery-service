from fastapi import APIRouter
from .v1 import packages_router

router_v1 = APIRouter(prefix="/api/v1", tags=["v1"])

router_v1.include_router(packages_router)
