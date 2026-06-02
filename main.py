from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger

from app.api.routes import router as license_router
from app.core.config import settings
from app.core.logging import configure_logging


def create_app() -> FastAPI:
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        description="API production-ready para consulta de cartas de conducao via scraping assincrono.",
        version="1.0.0",
        debug=settings.app_debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(license_router, prefix=settings.api_prefix)

    @app.get("/health", tags=["Saude"], summary="Health check")
    async def health_check() -> dict[str, str]:
        return {"status": "ok"}

    logger.info("{} started in {} mode", settings.app_name, settings.app_env)
    return app


app = create_app()
