# app/database.py

# Importa as ferramentas necessárias do SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Importa a função para carregar variáveis de ambiente
from dotenv import load_dotenv
import os

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Obtém a URL do banco de dados das variáveis de ambiente
# Se não encontrar, usa uma URL padrão (apenas para desenvolvimento/teste)
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://user:password@localhost:5432/test_db")

# Cria o "motor" do banco de dados.
# connect_args={"check_same_thread": False} é para SQLite, mas não atrapalha no PostgreSQL.
# echo=True mostra as queries SQL no terminal (útil para debug).
engine = create_engine(DATABASE_URL, echo=True)

# Cria uma sessão de banco de dados.
# autocommit=False: As mudanças não são salvas automaticamente.<br/>
# autoflush=False: Os objetos não são sincronizados automaticamente com o banco.<br/>
# bind=engine: Conecta esta sessão ao nosso motor de banco de dados.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base declarativa para os modelos. Todos os modelos herdarão dela.
Base = declarative_base()

# Função para obter uma sessão de banco de dados.
# É um "gerador" que abre uma sessão, a usa e depois a fecha,
# garantindo que os recursos do banco sejam liberados.
def get_db():
    db = SessionLocal() # Cria uma nova sessão
    try:
        yield db # Retorna a sessão para ser usada
    finally:
        db.close() # Garante que a sessão seja fechada no final