from sqlalchemy import text
from app.database import engine

sql_commands = [
    """
    CREATE TABLE IF NOT EXISTS password_reset_tokens (
        id SERIAL PRIMARY KEY,
        user_id INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE,
        token VARCHAR(100) NOT NULL UNIQUE,
        expires_at TIMESTAMP NOT NULL,
        used BOOLEAN DEFAULT FALSE NOT NULL,
        created_at TIMESTAMP DEFAULT NOW() NOT NULL
    );
    """,
    "CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_token ON password_reset_tokens(token);",
    "CREATE INDEX IF NOT EXISTS ix_password_reset_tokens_user_id ON password_reset_tokens(user_id);",
]

try:
    with engine.connect() as connection:
        for command in sql_commands:
            try:
                connection.execute(text(command))
                print(f"✅ Executado com sucesso")
            except Exception as e:
                print(f"⚠️  Aviso: {e}")

        connection.commit()
        print("\n✅ Migração de recuperação de senha concluída!")
except Exception as e:
    print(f"❌ Erro geral: {e}")
