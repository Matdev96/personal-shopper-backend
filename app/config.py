import os
from dotenv import load_dotenv

load_dotenv() #carrega as variáveis de ambiente do arquivo .env

# Configurações do banco de dados
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://user:password@localhost:5432/personal_shopper"
)

# Configurações de segurança
SECRET_KEY = os.getenv("SECRET_KEY", "sua_chave_secreta_aqui")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

#Configurações da aplicação
DEBUG = os.getenv("DEBUG", "True") == "True"
