"""
Models - Estrutura dos dados (tabelas do banco de dados)
Este arquivo importa todos os modelos para que possam ser facilmente acessados.
"""

# Importa cada modelo que você criou
from app.models.user import User
from app.models.category import Category
from app.models.product import Product
from app.models.cart import Cart, CartItem
from app.models.order import Order, OrderItem, OrderStatus
from app.models.product_request import ProductRequest, RequestStatus
from app.models.payment import Payment, PaymentType, PaymentStatus

__all__ = [
    "User",
    "Category",
    "Product",
    "Cart",
    "CartItem",
    "Order",
    "OrderItem",
    "OrderStatus",
    "ProductRequest",
    "RequestStatus",
    "Payment",
    "PaymentType",
    "PaymentStatus",
]