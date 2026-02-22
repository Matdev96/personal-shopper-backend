import sys
from pathlib import Path

# Adicionar o caminho correto ao sys.path
# Já estamos em personal-shopper-backend, então não precisa adicionar "backend"
current_path = Path(__file__).parent.parent
sys.path.insert(0, str(current_path))

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient

try:
    from app.main import app
    from app.database import Base
    from app.dependencies import get_db
    from app.models.user import User
    from app.models.product import Product
    from app.models.category import Category
    from app.models.order import Order, OrderItem, OrderStatus
    from app.models.cart import Cart, CartItem
except ImportError as e:
    print(f"Erro ao importar módulos: {e}")
    print(f"Caminho atual: {current_path}")
    print(f"sys.path: {sys.path}")
    raise

from datetime import datetime


# Configurar banco de dados de teste
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db():
    """Fixture para criar e limpar banco de dados de teste."""
    # Criar todas as tabelas
    Base.metadata.create_all(bind=engine)
    
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        # Limpar banco de dados após o teste
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session):
    """Fixture para criar cliente de teste."""
    def override_get_db():
        try:
            yield db
        finally:
            db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="function")
def test_user(db: Session):
    """Fixture para criar um usuário de teste."""
    user = User(
        email="test@example.com",
        full_name="Test User",
        hashed_password="hashed_password_123",
        is_admin=False,
        is_active=True,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture(scope="function")
def test_admin_user(db: Session):
    """Fixture para criar um usuário admin de teste."""
    admin = User(
        email="admin@example.com",
        full_name="Admin User",
        hashed_password="hashed_password_123",
        is_admin=True,
        is_active=True,
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    return admin


@pytest.fixture(scope="function")
def test_category(db: Session):
    """Fixture para criar uma categoria de teste."""
    category = Category(
        name="Test Category",
        description="This is a test category for testing purposes",
        is_active=True,
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@pytest.fixture(scope="function")
def test_product(db: Session, test_category: Category):
    """Fixture para criar um produto de teste."""
    product = Product(
        name="Test Product",
        description="This is a test product with detailed description",
        price=99.99,
        size="M",
        color="Blue",
        category_id=test_category.id,
        image_url="https://example.com/image.jpg",
        stock=100,
        is_active=True,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture(scope="function")
def test_cart(db: Session, test_user: User):
    """Fixture para criar um carrinho de teste."""
    cart = Cart(user_id=test_user.id)
    db.add(cart)
    db.commit()
    db.refresh(cart)
    return cart


@pytest.fixture(scope="function")
def test_cart_item(db: Session, test_cart: Cart, test_product: Product):
    """Fixture para criar um item de carrinho de teste."""
    cart_item = CartItem(
        cart_id=test_cart.id,
        product_id=test_product.id,
        quantity=2,
        price_at_time=test_product.price,
    )
    db.add(cart_item)
    db.commit()
    db.refresh(cart_item)
    return cart_item


@pytest.fixture(scope="function")
def test_order(db: Session, test_user: User, test_product: Product):
    """Fixture para criar um pedido de teste."""
    order = Order(
        user_id=test_user.id,
        total_price=test_product.price * 2,
        shipping_address="123 Test Street, Test City, Test Country",
        payment_method="credit_card",
        status=OrderStatus.PENDING,
    )
    db.add(order)
    db.flush()
    
    order_item = OrderItem(
        order_id=order.id,
        product_id=test_product.id,
        quantity=2,
        price_at_time=test_product.price,
    )
    db.add(order_item)
    db.commit()
    db.refresh(order)
    return order


@pytest.fixture(scope="function")
def auth_headers(test_user: User):
    """Fixture para gerar headers de autenticação."""
    # Nota: Você precisará implementar a geração de token JWT
    # Por enquanto, retornamos um dicionário vazio
    # Será implementado quando você tiver autenticação JWT
    return {"Authorization": "Bearer test_token"}