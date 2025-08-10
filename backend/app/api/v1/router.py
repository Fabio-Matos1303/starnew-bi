from fastapi import APIRouter

from .routes import health


api_router_v1 = APIRouter()

api_router_v1.include_router(health.router, tags=["health"])
