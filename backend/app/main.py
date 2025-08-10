from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .api.v1.router import api_router_v1


def create_app() -> FastAPI:
    application = FastAPI(title=settings.api_title, version=settings.api_version)

    # CORS (use wildcard by default; restrict via FRONTEND_ORIGIN if needed)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    application.include_router(api_router_v1, prefix="/api/v1")

    return application


app = create_app()
