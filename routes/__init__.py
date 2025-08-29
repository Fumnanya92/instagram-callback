"""Routes package for Grace Instagram callback app."""

from .web import router as web_router
from .api import router as api_router

__all__ = ["web_router", "api_router"]
