# tests/test_endpoints/test_cart.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ============================================================================
# FIXTURES AUXILIARES
# ============================================================================

@pytest.fixture
def user_token(client, test_user):
    """Fixture para obter token de usuário regular"""
    response = client.post(
        "/auth/login",
        json={
            "email": "test@example.com",
            "password": "TestPassword123!",
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def cart_item_payload(test_product):
    """Fixture com dados padrão de item do carrinho"""
    return {
        "product_id": test_product.id,
        "quantity": 2,
    }


# ============================================================================
# TESTES DE OBTENÇÃO DO CARRINHO
# ============================================================================

class TestGetCart:
    """Testes para obtenção do carrinho"""

    def test_get_cart_without_auth(self, client):
        """Teste: Obter carrinho sem autenticação"""
        response = client.get("/cart")
        assert response.status_code == 403

    def test_get_cart_not_found(self, client, user_token):
        """Teste: Obter carrinho que não existe"""
        response = client.get(
            "/cart",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "Carrinho não encontrado" in response.json()["detail"]

    def test_get_cart_with_items(self, client, user_token, test_product, db):
        """Teste: Obter carrinho com itens"""
        from app.models.cart import Cart, CartItem
        from app.models.user import User
        
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=2,
            price_at_time=test_product.price,
        )
        db.add(cart_item)
        db.commit()
        
        response = client.get(
            "/cart",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["user_id"] == user.id
        assert len(data["items"]) == 1


# ============================================================================
# TESTES DE LISTAGEM DE ITENS DO CARRINHO
# ============================================================================

class TestListCartItems:
    """Testes para listagem de itens do carrinho"""

    def test_list_cart_items_without_auth(self, client):
        """Teste: Listar itens sem autenticação"""
        response = client.get("/cart/items")
        assert response.status_code == 403

    def test_list_cart_items_cart_not_found(self, client, user_token):
        """Teste: Listar itens quando carrinho não existe"""
        response = client.get(
            "/cart/items",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "Carrinho não encontrado" in response.json()["detail"]

    def test_list_cart_items_empty(self, client, user_token, db):
        """Teste: Listar itens de carrinho vazio"""
        from app.models.cart import Cart
        from app.models.user import User
        
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.commit()
        
        response = client.get(
            "/cart/items",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_cart_items_with_pagination(self, client, user_token, test_product, db):
        """Teste: Listar itens com paginação"""
        from app.models.cart import Cart, CartItem
        from app.models.user import User
        
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
        
        for i in range(5):
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=test_product.id,
                quantity=i + 1,
                price_at_time=test_product.price,
            )
            db.add(cart_item)
        db.commit()
        
        response = client.get(
            "/cart/items?skip=0&limit=3",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3

    def test_list_cart_items_sort_by_price(self, client, user_token, test_product, db):
        """Teste: Listar itens ordenados por preço"""
        from app.models.cart import Cart, CartItem
        from app.models.user import User
        
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
        
        for i in range(3):
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=test_product.id,
                quantity=i + 1,
                price_at_time=test_product.price + i,
            )
            db.add(cart_item)
        db.commit()
        
        response = client.get(
            "/cart/items?sort_by=price_at_time&sort_order=asc",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 3


# ============================================================================
# TESTES DE ADIÇÃO DE ITENS AO CARRINHO
# ============================================================================

class TestAddItemToCart:
    """Testes para adição de itens ao carrinho"""

    def test_add_item_without_auth(self, client, cart_item_payload):
        """Teste: Adicionar item sem autenticação"""
        response = client.post("/cart/items", json=cart_item_payload)
        assert response.status_code == 403

    def test_add_item_product_not_found(self, client, user_token):
        """Teste: Adicionar item com produto inexistente"""
        response = client.post(
            "/cart/items",
            json={"product_id": 9999, "quantity": 1},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_add_item_invalid_product_id(self, client, user_token):
        """Teste: Adicionar item com ID de produto inválido"""
        response = client.post(
            "/cart/items",
            json={"product_id": -1, "quantity": 1},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 422

    def test_add_item_invalid_quantity(self, client, user_token, test_product):
        """Teste: Adicionar item com quantidade inválida"""
        response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 0},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 422

    def test_add_item_quantity_exceeds_limit(self, client, user_token, test_product):
        """Teste: Adicionar item com quantidade acima do limite"""
        response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1001},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 422

    def test_add_item_insufficient_stock(self, client, user_token, test_product):
        """Teste: Adicionar item com estoque insuficiente"""
        response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": test_product.stock + 1},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "Estoque insuficiente" in response.json()["detail"]

    def test_add_item_product_inactive(self, client, user_token, test_product, db):
        """Teste: Adicionar item com produto inativo"""
        from app.models.product import Product
        
        product = db.query(Product).filter(Product.id == test_product.id).first()
        product.is_active = False
        db.commit()
        
        response = client.post(
            "/cart/items",
            json={"product_id": product.id, "quantity": 1},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "não está disponível" in response.json()["detail"]

    def test_add_item_success(self, client, user_token, test_product):
        """Teste: Adicionar item com sucesso"""
        product_id = test_product.id
        product_price = test_product.price
        
        response = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 2},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["product_id"] == product_id
        assert data["quantity"] == 2
        assert data["price_at_time"] == product_price

    def test_add_item_update_existing(self, client, user_token, test_product):
        """Teste: Adicionar item que já existe (deve atualizar quantidade)"""
        product_id = test_product.id
        
        response1 = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 2},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response1.status_code == 201
        item_id = response1.json()["id"]
        
        response2 = client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 3},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response2.status_code == 201
        data = response2.json()
        assert data["id"] == item_id
        assert data["quantity"] == 5

    def test_add_item_creates_cart_if_not_exists(self, client, user_token, test_product):
        """Teste: Adicionar item cria carrinho se não existir"""
        response = client.post(
            "/cart/items",
            json={"product_id": test_product.id, "quantity": 1},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        
        cart_response = client.get(
            "/cart",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert cart_response.status_code == 200


# ============================================================================
# TESTES DE ATUALIZAÇÃO DE ITENS DO CARRINHO
# ============================================================================

class TestUpdateCartItem:
    """Testes para atualização de itens do carrinho"""

    def test_update_item_without_auth(self, client):
        """Teste: Atualizar item sem autenticação"""
        response = client.put("/cart/items/1?quantity=5")
        assert response.status_code == 403

    def test_update_item_invalid_item_id(self, client, user_token):
        """Teste: Atualizar item com ID inválido"""
        response = client.put(
            "/cart/items/-1?quantity=5",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "deve ser um número positivo" in response.json()["detail"]

    def test_update_item_invalid_quantity(self, client, user_token):
        """Teste: Atualizar item com quantidade inválida"""
        response = client.put(
            "/cart/items/1?quantity=0",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "maior que zero" in response.json()["detail"]

    def test_update_item_quantity_exceeds_limit(self, client, user_token):
        """Teste: Atualizar item com quantidade acima do limite"""
        response = client.put(
            "/cart/items/1?quantity=1001",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "não pode exceder 1000" in response.json()["detail"]

    def test_update_item_not_found(self, client, user_token):
        """Teste: Atualizar item que não existe"""
        response = client.put(
            "/cart/items/9999?quantity=5",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_update_item_insufficient_stock(self, client, user_token, test_product, db):
        """Teste: Atualizar item com estoque insuficiente"""
        from app.models.cart import Cart, CartItem
        from app.models.user import User
        
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=1,
            price_at_time=test_product.price,
        )
        db.add(cart_item)
        db.commit()
        
        response = client.put(
            f"/cart/items/{cart_item.id}?quantity={test_product.stock + 1}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "Estoque insuficiente" in response.json()["detail"]

    def test_update_item_success(self, client, user_token, test_product, db):
        """Teste: Atualizar item com sucesso"""
        from app.models.cart import Cart, CartItem
        from app.models.user import User
        
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=2,
            price_at_time=test_product.price,
        )
        db.add(cart_item)
        db.commit()
        
        response = client.put(
            f"/cart/items/{cart_item.id}?quantity=5",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["quantity"] == 5


# ============================================================================
# TESTES DE REMOÇÃO DE ITENS DO CARRINHO
# ============================================================================

class TestRemoveCartItem:
    """Testes para remoção de itens do carrinho"""

    def test_remove_item_without_auth(self, client):
        """Teste: Remover item sem autenticação"""
        response = client.delete("/cart/items/1")
        assert response.status_code == 403

    def test_remove_item_not_found(self, client, user_token):
        """Teste: Remover item que não existe"""
        response = client.delete(
            "/cart/items/9999",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_remove_item_success(self, client, user_token, test_product, db):
        """Teste: Remover item com sucesso"""
        from app.models.cart import Cart, CartItem
        from app.models.user import User
        
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
        
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=test_product.id,
            quantity=2,
            price_at_time=test_product.price,
        )
        db.add(cart_item)
        db.commit()
        
        item_id = cart_item.id
        
        response = client.delete(
            f"/cart/items/{item_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 204
        
        verify_response = client.get(
            "/cart/items",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert len(data) == 0


# ============================================================================
# TESTES DE LIMPEZA DO CARRINHO
# ============================================================================

class TestClearCart:
    """Testes para limpeza do carrinho"""

    def test_clear_cart_without_auth(self, client):
        """Teste: Limpar carrinho sem autenticação"""
        response = client.delete("/cart")
        assert response.status_code == 403

    def test_clear_cart_not_found(self, client, user_token):
        """Teste: Limpar carrinho que não existe"""
        response = client.delete(
            "/cart",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "Carrinho não encontrado" in response.json()["detail"]

    def test_clear_cart_success(self, client, user_token, test_product, db):
        """Teste: Limpar carrinho com sucesso"""
        from app.models.cart import Cart, CartItem
        from app.models.user import User
        
        user = db.query(User).filter(User.email == "test@example.com").first()
        
        cart = Cart(user_id=user.id)
        db.add(cart)
        db.flush()
        
        for i in range(3):
            cart_item = CartItem(
                cart_id=cart.id,
                product_id=test_product.id,
                quantity=i + 1,
                price_at_time=test_product.price,
            )
            db.add(cart_item)
        db.commit()
        
        response = client.delete(
            "/cart",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 204
        
        verify_response = client.get(
            "/cart/items",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert verify_response.status_code == 200
        data = verify_response.json()
        assert len(data) == 0