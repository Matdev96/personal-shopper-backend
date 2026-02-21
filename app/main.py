from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from app.database import Base, engine
from app.core.config import settings
from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.routers import auth_router, categories_router, products_router, stock_router, cart_router, orders_router

# Criar as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

# Criar a aplicação FastAPI
app = FastAPI(
    title="Personal Shopper API",
    description="API para e-commerce de personal shopper",
    version="1.0.0",
)

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Criar diretório de uploads se não existir
uploads_dir = Path("uploads")
uploads_dir.mkdir(exist_ok=True)

# Servir arquivos estáticos (imagens)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ============================================================================
# INCLUIR ROUTERS
# ============================================================================

app.include_router(auth_router)
app.include_router(categories_router)
app.include_router(products_router)
app.include_router(stock_router)
app.include_router(cart_router)
app.include_router(orders_router)


# ============================================================================
# ROTAS PÚBLICAS
# ============================================================================

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raiz da API.
    """
    return {
        "message": "Bem-vindo à Personal Shopper API",
        "version": "1.0.0",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Verificar se a API está funcionando.
    """
    return {
        "status": "ok",
        "message": "API está funcionando corretamente",
    }