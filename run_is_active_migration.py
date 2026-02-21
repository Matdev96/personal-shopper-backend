from sqlalchemy import text
from app.database import engine

# SQL commands para adicionar a coluna is_active
sql_commands = [
    "ALTER TABLE products ADD COLUMN IF NOT EXISTS is_active BOOLEAN DEFAULT TRUE NOT NULL;"
]

# Executar o script SQL
try:
    with engine.connect() as connection:
        for command in sql_commands:
            try:
                connection.execute(text(command))
                print(f"✅ Executado: {command[:60]}...")
            except Exception as e:
                print(f"⚠️  Aviso: {command[:60]}...")
                print(f"   Detalhes: {e}")
        
        # Confirmar as mudanças
        connection.commit()
        print("\n✅ Migração concluída com sucesso!")
except Exception as e:
    print(f"❌ Erro geral: {e}")
