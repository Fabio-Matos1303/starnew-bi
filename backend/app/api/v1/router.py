from fastapi import APIRouter

from .routes import health, os as os_routes, kpi as kpi_routes, vendas as vendas_routes, locacoes as loc_routes


api_router_v1 = APIRouter()

api_router_v1.include_router(health.router, tags=["health"])
api_router_v1.include_router(os_routes.router, tags=["os"])
api_router_v1.include_router(kpi_routes.router, tags=["kpi"])
api_router_v1.include_router(vendas_routes.router, tags=["vendas"])
api_router_v1.include_router(loc_routes.router, tags=["locacoes"])
