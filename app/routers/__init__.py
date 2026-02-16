# app/routers/__init__.py

"""
Routers - Endpoints da aplicação
"""

from app.routers.auth import router as auth_router

__all__ = ["auth_router"]