"""
Routers - Endpoints da aplicação
"""

from app.routers.auth import router as auth_router
from app.routers.categories import router as categories_router
from app.routers.products import router as products_router
from app.routers.stock import router as stock_router
from app.routers.cart import router as cart_router
from app.routers.orders import router as orders_router
from app.routers.admin_users import router as admin_users_router
from app.routers.admin_products import router as admin_products_router


__all__ = ["auth_router", "categories_router", "products_router", "stock_router", "cart_router", "orders_router", "admin_users_router", "admin_products_router"]