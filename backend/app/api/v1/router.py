from fastapi import APIRouter

from .routes import health, os as os_routes


api_router_v1 = APIRouter()

api_router_v1.include_router(health.router, tags=["health"])
api_router_v1.include_router(os_routes.router, tags=["os"])
