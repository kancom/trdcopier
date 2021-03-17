from fastapi import APIRouter

from .endpoints import auth, config, info

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth")
api_router.include_router(info.router, prefix="/info")
api_router.include_router(config.router, prefix="/config")
