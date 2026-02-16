# app/routers/__init__.py

"""
Routers - Endpoints da aplicação
"""

from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router

__all__ = ["auth_router", "categories_router", "products_router"]