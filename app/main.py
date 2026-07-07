from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.compare import router as compare_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.web.router import router as web_router

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "web" / "static"


@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("%s starting in %s mode", settings.app_name, settings.app_env)
    yield
    logger.info("%s shutting down", settings.app_name)


def create_app() -> FastAPI:
    configure_logging(settings)

    app = FastAPI(
        title=settings.app_name,
        debug=settings.app_debug,
        version="0.1.0",
        lifespan=lifespan,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.api_v1_prefix}/openapi.json",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

    app.include_router(api_router, prefix=settings.api_v1_prefix)
    app.include_router(compare_router)
    app.include_router(web_router)
    return app


app = create_app()
