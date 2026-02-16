from app.database import SessionLocal
from app.models.user import User

session = SessionLocal()
users = session.query(User).all()

print(f"Total de usuários: {len(users)}")
print("-" * 50)

for user in users:
    print(f"ID: {user.id}")
    print(f"Email: {user.email}")
    print(f"Username: {user.username}")
    print(f"Full Name: {user.full_name}")
    print(f"Is Active: {user.is_active}")
    print(f"Is Admin: {user.is_admin}")
    print(f"Hashed Password: {user.hashed_password[:20]}...")
    print("-" * 50)

session.close()