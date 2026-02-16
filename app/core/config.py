# app/core/config.py

from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    """
    Configurações da aplicação.
    Carrega variáveis do arquivo .env
    """
    
    # Banco de dados
    DATABASE_URL: str
    
    # Segurança
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Debug
    DEBUG: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = True

# Instância global das configurações
settings = Settings()