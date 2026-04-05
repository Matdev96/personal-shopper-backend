from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from slowapi.errors import RateLimitExceeded
from slowapi import _rate_limit_exceeded_handler
from pathlib import Path
import os

from app.database import Base, engine
from app.core.config import settings
from app.core.limiter import limiter
from app.routers import (
    auth_router,
    categories_router,
    products_router,
    stock_router,
    cart_router,
    orders_router,
    admin_users_router,
    admin_products_router,
    requests_router,
    payments_router,
    admin_requests_router,
)

# ============================================================================
# CRIAR AS TABELAS NO BANCO DE DADOS
# ============================================================================

Base.metadata.create_all(bind=engine)

# ============================================================================
# CRIAR A APLICAÇÃO FASTAPI
# ============================================================================

app = FastAPI(
    title="Personal Shopper API",
    description="API para e-commerce de personal shopper",
    version="1.0.0",
)

# Registra o rate limiter na aplicação e define o handler de erro 429
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# ============================================================================
# CONFIGURAR CORS
# ============================================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# CONFIGURAR ARQUIVOS ESTÁTICOS
# ============================================================================

# Criar diretório de uploads se não existir
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

# Criar subdiretórios
(UPLOAD_DIR / "products").mkdir(exist_ok=True)
(UPLOAD_DIR / "users").mkdir(exist_ok=True)

# Servir arquivos estáticos (imagens)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# ============================================================================
# INCLUIR ROUTERS
# ============================================================================

app.include_router(auth_router, prefix="/api/v1")
app.include_router(categories_router, prefix="/api/v1")
app.include_router(products_router, prefix="/api/v1")
app.include_router(stock_router, prefix="/api/v1")
app.include_router(cart_router, prefix="/api/v1")
app.include_router(orders_router, prefix="/api/v1")
app.include_router(admin_users_router, prefix="/api/v1")
app.include_router(admin_products_router, prefix="/api/v1")
app.include_router(requests_router, prefix="/api/v1")
app.include_router(payments_router, prefix="/api/v1")
app.include_router(admin_requests_router, prefix="/api/v1")

# ============================================================================
# ROTAS PÚBLICAS
# ============================================================================

@app.get("/", tags=["Root"])
def read_root():
    """
    Endpoint raiz da API.
    Retorna informações sobre a API.
    """
    return {
        "message": "Bem-vindo à Personal Shopper API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Verificar se a API está funcionando.
    Útil para monitoramento e health checks.
    """
    return {
        "status": "ok",
        "message": "API está funcionando corretamente",
    }