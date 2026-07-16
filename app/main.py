import logging
from contextlib import asynccontextmanager
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.v1.endpoints.compare import router as compare_router
from app.api.v1.router import api_router
from app.core.config import settings
from app.core.logging import configure_logging, logger
from app.web.router import router as web_router

load_dotenv()

APP_DIR = Path(__file__).resolve().parent
STATIC_DIR = APP_DIR / "web" / "static"

# ==========================================
# 🛠️ DYNAMIC UVICORN LOGGING PATCH (CRASH PROOF)
# ==========================================
class UvicornLogFilter(logging.Filter):
    def filter(self, record):
        # Jo bhi fields aapka custom custom logger ya formatters mang sakte hain, unhe safe fallback dein
        required_fields = {
            "client_addr": "-",
            "request_line": getattr(record, "args", [""])[1] if len(getattr(record, "args", [])) > 1 else "-",
            "status_code": getattr(record, "args", [""])[4] if len(getattr(record, "args", [])) > 4 else "-",
            "method": getattr(record, "args", [""])[1] if len(getattr(record, "args", [])) > 1 else "-",
        }
        
        for field, default in required_fields.items():
            if not hasattr(record, field):
                setattr(record, field, default)
                
        return True

def apply_log_patch():
    # Uvicorn ke har tarah ke logger aur handlers me cross-contamination rokein
    for logger_name in ("uvicorn", "uvicorn.access", "uvicorn.error", "uvicorn.asgi"):
        uvicorn_logger = logging.getLogger(logger_name)
        uvicorn_logger.addFilter(UvicornLogFilter())
        for handler in uvicorn_logger.handlers:
            handler.addFilter(UvicornLogFilter())

# Pehle hi patch apply kar dein
apply_log_patch()
# ==========================================

@asynccontextmanager
async def lifespan(_: FastAPI):
    logger.info("%s starting in %s mode", settings.app_name, settings.app_env)
    yield
    logger.info("%s shutting down", settings.app_name)

def create_app() -> FastAPI:
    configure_logging(settings)

    # configure_logging chalne ke BAAD dubara patch apply karna zaroori hai
    apply_log_patch()

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