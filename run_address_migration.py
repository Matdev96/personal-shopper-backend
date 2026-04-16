from sqlalchemy import text
from app.database import engine

sql_commands = [
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS cep VARCHAR(9);",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS logradouro VARCHAR(200);",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS numero VARCHAR(20);",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS complemento VARCHAR(100);",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS bairro VARCHAR(100);",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS cidade VARCHAR(100);",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS estado VARCHAR(2);",
    "ALTER TABLE users ADD COLUMN IF NOT EXISTS retirar_na_loja BOOLEAN DEFAULT FALSE;",
]

try:
    with engine.connect() as connection:
        for command in sql_commands:
            try:
                connection.execute(text(command))
                print(f"✅ Executado: {command[:60]}...")
            except Exception as e:
                print(f"⚠️  Aviso: {command[:60]}...")
                print(f"   Detalhes: {e}")

        connection.commit()
        print("\n✅ Migração de endereço concluída com sucesso!")
except Exception as e:
    print(f"❌ Erro geral: {e}")
