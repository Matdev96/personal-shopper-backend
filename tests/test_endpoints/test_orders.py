import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session
from datetime import datetime, timedelta


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
def order_payload(test_product):
    """Fixture com dados padrão de pedido"""
    return {
        "items": [
            {
                "product_id": test_product.id,
                "quantity": 2,
            }
        ],
        "shipping_address": "Rua das Flores, 123, São Paulo, SP",
        "payment_method": "credit_card",
    }


# ============================================================================
# TESTES DE LISTAGEM DE PEDIDOS
# ============================================================================

class TestListOrders:
    """Testes para listagem de pedidos"""

    def test_list_orders_without_auth(self, client):
        """Teste: Listar pedidos sem autenticação"""
        response = client.get("/orders")
        assert response.status_code == 403

    def test_list_orders_empty(self, client, user_token):
        """Teste: Listar pedidos quando não há nenhum"""
        response = client.get(
            "/orders",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) == 0

    def test_list_orders_with_pagination(self, client, user_token, test_product):
        """Teste: Listar pedidos com paginação"""
        product_id = test_product.id
        
        for i in range(3):
            client.post(
                "/orders",
                json={
                    "items": [{"product_id": product_id, "quantity": 1}],
                    "shipping_address": f"Rua {i}, 123",
                    "payment_method": "credit_card",
                },
                headers={"Authorization": f"Bearer {user_token}"},
            )
        
        response = client.get(
            "/orders?skip=0&limit=2",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) <= 2

    def test_list_orders_filter_by_status(self, client, user_token, test_product):
        """Teste: Listar pedidos filtrados por status"""
        product_id = test_product.id
        
        client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        
        response = client.get(
            "/orders?status_filter=pending",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert len(data) > 0
        assert all(order["status"] == "pending" for order in data)

    def test_list_orders_filter_by_price_range(self, client, user_token, test_product):
        """Teste: Listar pedidos filtrados por faixa de preço"""
        product_id = test_product.id
        
        client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        
        response = client.get(
            "/orders?min_price=50&max_price=500",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_orders_sort_by_price(self, client, user_token):
        """Teste: Listar pedidos ordenados por preço"""
        response = client.get(
            "/orders?sort_by=total_price&sort_order=asc",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_orders_invalid_limit(self, client, user_token):
        """Teste: Listar pedidos com limite inválido"""
        response = client.get(
            "/orders?limit=200",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200


# ============================================================================
# TESTES DE OBTENÇÃO DE PEDIDO
# ============================================================================

class TestGetOrder:
    """Testes para obtenção de um pedido específico"""

    def test_get_order_without_auth(self, client):
        """Teste: Obter pedido sem autenticação"""
        response = client.get("/orders/1")
        assert response.status_code == 403

    def test_get_order_not_found(self, client, user_token):
        """Teste: Obter pedido que não existe"""
        response = client.get(
            "/orders/9999",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_get_order_success(self, client, user_token, test_product):
        """Teste: Obter pedido com sucesso"""
        product_id = test_product.id
        
        create_response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert create_response.status_code == 201
        order_id = create_response.json()["id"]
        
        response = client.get(
            f"/orders/{order_id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == order_id
        assert data["status"] == "pending"


# ============================================================================
# TESTES DE CRIAÇÃO DE PEDIDO
# ============================================================================

class TestCreateOrder:
    """Testes para criação de pedidos"""

    def test_create_order_without_auth(self, client, order_payload):
        """Teste: Criar pedido sem autenticação"""
        response = client.post("/orders", json=order_payload)
        assert response.status_code == 403

    def test_create_order_empty_items(self, client, user_token):
        """Teste: Criar pedido sem itens"""
        response = client.post(
            "/orders",
            json={
                "items": [],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 422

    def test_create_order_product_not_found(self, client, user_token):
        """Teste: Criar pedido com produto inexistente"""
        response = client.post(
            "/orders",
            json={
                "items": [{"product_id": 9999, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_create_order_product_inactive(self, client, user_token, test_product, db):
        """Teste: Criar pedido com produto inativo"""
        from app.models.product import Product
        
        product = db.query(Product).filter(Product.id == test_product.id).first()
        product.is_active = False
        db.commit()
        
        response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product.id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "não está disponível" in response.json()["detail"]

    def test_create_order_insufficient_stock(self, client, user_token, test_product):
        """Teste: Criar pedido com estoque insuficiente"""
        response = client.post(
            "/orders",
            json={
                "items": [{"product_id": test_product.id, "quantity": test_product.stock + 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "Estoque insuficiente" in response.json()["detail"]

    def test_create_order_duplicate_products(self, client, user_token, test_product):
        """Teste: Criar pedido com produtos duplicados"""
        response = client.post(
            "/orders",
            json={
                "items": [
                    {"product_id": test_product.id, "quantity": 1},
                    {"product_id": test_product.id, "quantity": 1},
                ],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "aparece mais de uma vez" in response.json()["detail"]

    def test_create_order_missing_shipping_address(self, client, user_token, test_product):
        """Teste: Criar pedido sem endereço de entrega"""
        response = client.post(
            "/orders",
            json={
                "items": [{"product_id": test_product.id, "quantity": 1}],
                "shipping_address": "",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 422

    def test_create_order_success(self, client, user_token, test_product):
        """Teste: Criar pedido com sucesso"""
        product_id = test_product.id
        
        response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 2}],
                "shipping_address": "Rua das Flores, 123, São Paulo, SP",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["status"] == "pending"
        assert data["shipping_address"] == "Rua das Flores, 123, São Paulo, SP"
        assert data["payment_method"] == "credit_card"
        assert len(data["items"]) == 1

    def test_create_order_clears_cart(self, client, user_token, test_product):
        """Teste: Criar pedido limpa o carrinho"""
        product_id = test_product.id
        
        client.post(
            "/cart/items",
            json={"product_id": product_id, "quantity": 1},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        
        response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        
        cart_response = client.get(
            "/cart/items",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert cart_response.status_code == 200
        data = cart_response.json()
        assert len(data) == 0

    def test_create_order_updates_stock(self, client, user_token, test_product, db):
        """Teste: Criar pedido atualiza o estoque"""
        from app.models.product import Product
        
        initial_stock = test_product.stock
        quantity = 2
        product_id = test_product.id
        
        response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": quantity}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 201
        
        product = db.query(Product).filter(Product.id == product_id).first()
        assert product.stock == initial_stock - quantity


# ============================================================================
# TESTES DE CANCELAMENTO DE PEDIDO
# ============================================================================

class TestCancelOrder:
    """Testes para cancelamento de pedidos"""

    def test_cancel_order_without_auth(self, client):
        """Teste: Cancelar pedido sem autenticação"""
        response = client.put("/orders/1/cancel")
        assert response.status_code == 403

    def test_cancel_order_not_found(self, client, user_token):
        """Teste: Cancelar pedido que não existe"""
        response = client.put(
            "/orders/9999/cancel",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_cancel_order_success(self, client, user_token, test_product):
        """Teste: Cancelar pedido com sucesso"""
        product_id = test_product.id
        
        create_response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert create_response.status_code == 201
        order_id = create_response.json()["id"]
        
        response = client.put(
            f"/orders/{order_id}/cancel",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "cancelled"

    def test_cancel_order_restores_stock(self, client, user_token, test_product, db):
        """Teste: Cancelar pedido restaura o estoque"""
        from app.models.product import Product
        
        initial_stock = test_product.stock
        quantity = 2
        product_id = test_product.id
        
        create_response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": quantity}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        order_id = create_response.json()["id"]
        
        product = db.query(Product).filter(Product.id == product_id).first()
        assert product.stock == initial_stock - quantity
        
        response = client.put(
            f"/orders/{order_id}/cancel",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        
        product = db.query(Product).filter(Product.id == product_id).first()
        assert product.stock == initial_stock

    def test_cancel_order_already_confirmed(self, client, user_token, test_product, db):
        """Teste: Cancelar pedido com status confirmed (deve falhar)"""
        from app.models.order import Order
        
        product_id = test_product.id
        
        create_response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        order_id = create_response.json()["id"]
        
        order = db.query(Order).filter(Order.id == order_id).first()
        order.status = "confirmed"
        db.commit()
        
        response = client.put(
            f"/orders/{order_id}/cancel",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "não pode ser cancelado" in response.json()["detail"]


# ============================================================================
# TESTES DE STATUS DO PEDIDO
# ============================================================================

class TestOrderStatus:
    """Testes para verificação e atualização de status"""

    def test_get_order_status_without_auth(self, client):
        """Teste: Obter status sem autenticação"""
        response = client.get("/orders/1/status")
        assert response.status_code == 403

    def test_get_order_status_not_found(self, client, user_token):
        """Teste: Obter status de pedido inexistente"""
        response = client.get(
            "/orders/9999/status",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_get_order_status_success(self, client, user_token, test_product):
        """Teste: Obter status com sucesso"""
        product_id = test_product.id
        
        create_response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        order_id = create_response.json()["id"]
        
        response = client.get(
            f"/orders/{order_id}/status",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["order_id"] == order_id
        assert data["status"] == "pending"
        assert "created_at" in data
        assert "updated_at" in data

    def test_update_order_status_without_auth(self, client):
        """Teste: Atualizar status sem autenticação"""
        response = client.put("/orders/1/status?new_status=confirmed")
        assert response.status_code == 403

    def test_update_order_status_not_found(self, client, user_token):
        """Teste: Atualizar status de pedido inexistente"""
        response = client.put(
            "/orders/9999/status?new_status=confirmed",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]

    def test_update_order_status_invalid_status(self, client, user_token, test_product):
        """Teste: Atualizar com status inválido"""
        product_id = test_product.id
        
        create_response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        order_id = create_response.json()["id"]
        
        response = client.put(
            f"/orders/{order_id}/status?new_status=invalid_status",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 400
        assert "Status inválido" in response.json()["detail"]

    def test_update_order_status_success(self, client, user_token, test_product):
        """Teste: Atualizar status com sucesso"""
        product_id = test_product.id
        
        create_response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        order_id = create_response.json()["id"]
        
        response = client.put(
            f"/orders/{order_id}/status?new_status=confirmed",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "confirmed"

    def test_update_order_status_to_delivered(self, client, user_token, test_product):
        """Teste: Atualizar status para delivered"""
        product_id = test_product.id
        
        create_response = client.post(
            "/orders",
            json={
                "items": [{"product_id": product_id, "quantity": 1}],
                "shipping_address": "Rua das Flores, 123",
                "payment_method": "credit_card",
            },
            headers={"Authorization": f"Bearer {user_token}"},
        )
        order_id = create_response.json()["id"]
        
        client.put(
            f"/orders/{order_id}/status?new_status=confirmed",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        
        client.put(
            f"/orders/{order_id}/status?new_status=shipped",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        
        response = client.put(
            f"/orders/{order_id}/status?new_status=delivered",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "delivered"