# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import DATABASE_URL

# Criar a engine (motor) que conecta ao banco de dados
engine = create_engine(
    DATABASE_URL,
    echo=True
)

# SessionLocal = fábrica de sessões
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base = classe base para todos os modelos
Base = declarative_base()

# Função para obter a sessão do banco de dados
def get_db():
    """
    Dependency que fornece uma sessão do banco de dados.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        