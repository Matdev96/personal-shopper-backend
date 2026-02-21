from sqlalchemy.orm import Session
from app.database import engine
from app.models.user import User
from app.core.security import hash_password

# Criar uma sessão
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

try:
    # Buscar o usuário admin
    admin = db.query(User).filter(User.email == "admin@example.com").first()
    
    if admin:
        # Resetar a senha para "admin123"
        admin.hashed_password = hash_password("admin123")
        db.commit()
        print("✅ Senha do admin resetada para 'admin123'")
    else:
        print("❌ Usuário admin não encontrado")
except Exception as e:
    print(f"❌ Erro ao resetar a senha: {e}")
finally:
    db.close()
