import logging
from logging.config import dictConfig

from app.core.config import Settings


def configure_logging(settings: Settings) -> None:
    log_level = settings.log_level.upper()

    dictConfig(
        {
            "version": 1,
            "disable_existing_loggers": False,
            "formatters": {
                "default": {
                    "format": "%(asctime)s | %(levelname)s | %(name)s | %(message)s",
                },
                "access": {
                    "format": "%(asctime)s | %(levelname)s | %(client_addr)s | %(request_line)s | %(status_code)s",
                },
            },
            "handlers": {
                "default": {
                    "class": "logging.StreamHandler",
                    "formatter": "default",
                },
                "access": {
                    "class": "logging.StreamHandler",
                    "formatter": "access",
                },
            },
            "loggers": {
                "app": {"handlers": ["default"], "level": log_level, "propagate": False},
                "uvicorn": {"handlers": ["default"], "level": log_level, "propagate": False},
                "uvicorn.error": {"handlers": ["default"], "level": log_level, "propagate": False},
                "uvicorn.access": {"handlers": ["access"], "level": log_level, "propagate": False},
            },
            "root": {"handlers": ["default"], "level": log_level},
        }
    )


logger = logging.getLogger("app")

