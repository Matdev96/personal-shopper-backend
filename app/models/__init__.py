# app/models/__init__.py

"""
Models - Estrutura dos dados (tabelas do banco de dados)
Este arquivo importa todos os modelos para que possam ser facilmente acessados.
"""

# Importa cada modelo que você criou
from app.models.user import User
from app.models.category import Category
from app.models.product import Product

# Define quais modelos serão exportados quando 'app.models' for importado
__all__ = ["User", "Category", "Product"]