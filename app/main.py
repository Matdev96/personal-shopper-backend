# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# Importa a base declarativa e o motor do banco de dados
from app.database import Base, engine

# Importa todos os modelos para que o SQLAlchemy os reconheça
from app.models import user, category, product  # noqa: F401

# Cria todas as tabelas no banco de dados (se não existirem)
# Isso é feito aqui para garantir que as tabelas sejam criadas
# quando a aplicação FastAPI for iniciada.
Base.metadata.create_all(bind=engine)

# Cria a instância da aplicação FastAPI
app = FastAPI(
    title="Personal Shopper API",
    description="API backend para gerenciar compras de personal shopper.",
    version="0.1.0",
)

# Configurar CORS (permitir requisições do frontend)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Endpoint de saúde para verificar se a API está funcionando
@app.get("/health", tags=["Health Check"])
async def health_check():
    """
    Verifica se a API está funcionando corretamente.
    """
    return {"status": "healthy"}

# Endpoint raiz
@app.get("/", tags=["Root"])
async def read_root():
    """
    Endpoint raiz da API.
    Retorna uma mensagem de boas-vindas.
    """
    return {"message": "Bem-vindo à Personal Shopper API!"}