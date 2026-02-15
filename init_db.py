# init_db.py

"""
Script para criar as tabelas no banco de dados.
Execute: python init_db.py
"""

# Importa a base declarativa e o motor do banco de dados
from app.database import Base, engine
# Importa todos os modelos para que o SQLAlchemy os reconheça
from app.models.user import User
from app.models.category import Category
from app.models.product import Product

def init_db():
    """
    Cria todas as tabelas no banco de dados.
    """
    print("🔄 Criando tabelas no banco de dados...")
    # Base.metadata.create_all() é o comando mágico que cria as tabelas
    # para todos os modelos que herdam de 'Base'
    Base.metadata.create_all(bind=engine)
    print("✅ Tabelas criadas com sucesso!")

if __name__ == "__main__":
    init_db()