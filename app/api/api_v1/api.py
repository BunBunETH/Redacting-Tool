from fastapi import APIRouter
from app.api.api_v1.endpoints import intercom, vault

api_router = APIRouter()
api_router.include_router(intercom.router, prefix="/intercom", tags=["intercom"])
api_router.include_router(vault.router, prefix="/vault", tags=["vault"]) 