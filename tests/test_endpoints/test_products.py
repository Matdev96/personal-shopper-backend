# tests/test_endpoints/test_products.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


# ============================================================================
# FIXTURES AUXILIARES
# ============================================================================

@pytest.fixture
def admin_token(client, test_admin_user):
    """Fixture para obter token de admin"""
    response = client.post(
        "/auth/login",
        json={
            "email": "admin@example.com",
            "password": "AdminPassword123!",
        },
    )
    return response.json()["access_token"]


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
def product_payload(test_category):
    """Fixture com dados padrão de produto"""
    return {
        "name": "Test Product",
        "description": "A test product",
        "price": 99.99,
        "size": "M",
        "color": "Blue",
        "category_id": test_category.id,
        "image_url": "https://example.com/image.jpg",
        "stock": 100,
    }


# ============================================================================
# TESTES DE CRIAÇÃO DE PRODUTOS
# ============================================================================

class TestProductCreation:
    """Testes para criação de produtos"""

    def test_create_product_as_admin(self, client, admin_token, product_payload):
        """Teste: Criar produto como admin"""
        response = client.post(
            "/products",
            json=product_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == product_payload["name"]
        assert data["price"] == product_payload["price"]
        assert data["stock"] == product_payload["stock"]
        assert data["is_active"] is True

    def test_create_product_without_auth(self, client, product_payload):
        """Teste: Criar produto sem autenticação"""
        response = client.post("/products", json=product_payload)
        assert response.status_code == 403

    def test_create_product_as_regular_user(self, client, user_token, product_payload):
        """Teste: Criar produto como usuário regular (deve falhar)"""
        response = client.post(
            "/products",
            json=product_payload,
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403

    def test_create_product_invalid_category(self, client, admin_token, product_payload):
        """Teste: Criar produto com categoria inválida"""
        product_payload["category_id"] = 9999
        response = client.post(
            "/products",
            json=product_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404
        assert "não encontrada" in response.json()["detail"]

    def test_create_product_duplicate_name_same_category(
        self, client, admin_token, test_product, product_payload
    ):
        """Teste: Criar produto com nome duplicado na mesma categoria"""
        product_payload["name"] = test_product.name
        product_payload["category_id"] = test_product.category_id
        
        response = client.post(
            "/products",
            json=product_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 400
        assert "Já existe um produto" in response.json()["detail"]

    def test_create_product_missing_required_fields(self, client, admin_token):
        """Teste: Criar produto sem campos obrigatórios"""
        response = client.post(
            "/products",
            json={"name": "Test Product"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422

    def test_create_product_invalid_price(self, client, admin_token, product_payload):
        """Teste: Criar produto com preço inválido"""
        product_payload["price"] = -10.00
        response = client.post(
            "/products",
            json=product_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422

    def test_create_product_invalid_stock(self, client, admin_token, product_payload):
        """Teste: Criar produto com estoque inválido"""
        product_payload["stock"] = -5
        response = client.post(
            "/products",
            json=product_payload,
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422


# ============================================================================
# TESTES DE LISTAGEM DE PRODUTOS
# ============================================================================

class TestProductListing:
    """Testes para listagem de produtos"""

    def test_list_products(self, client, test_product):
        """Teste: Listar produtos"""
        response = client.get("/products")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) > 0

    def test_list_products_with_pagination(self, client, test_product):
        """Teste: Listar produtos com paginação"""
        response = client.get("/products?skip=0&limit=5")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_products_filter_by_category(self, client, test_product):
        """Teste: Listar produtos filtrados por categoria"""
        response = client.get(f"/products?category_id={test_product.category_id}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 0:
            assert all(p["category_id"] == test_product.category_id for p in data)

    def test_list_products_filter_by_price_range(self, client, test_product):
        """Teste: Listar produtos filtrados por faixa de preço"""
        response = client.get("/products?min_price=50&max_price=150")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_products_filter_in_stock(self, client, test_product):
        """Teste: Listar apenas produtos em estoque"""
        response = client.get("/products?in_stock=true")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_products_search(self, client, test_product):
        """Teste: Buscar produtos por nome"""
        response = client.get(f"/products?search={test_product.name}")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_products_sort_by_price_asc(self, client, test_product):
        """Teste: Listar produtos ordenados por preço (ascendente)"""
        response = client.get("/products?sort_by=price&sort_order=asc")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        if len(data) > 1:
            prices = [p["price"] for p in data]
            assert prices == sorted(prices)

    def test_list_products_sort_by_price_desc(self, client, test_product):
        """Teste: Listar produtos ordenados por preço (descendente)"""
        response = client.get("/products?sort_by=price&sort_order=desc")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)

    def test_list_products_invalid_limit(self, client):
        """Teste: Listar produtos com limite inválido"""
        response = client.get("/products?limit=200")
        assert response.status_code == 200


# ============================================================================
# TESTES DE OBTENÇÃO DE PRODUTO
# ============================================================================

class TestProductRetrieval:
    """Testes para obtenção de um produto específico"""

    def test_get_product(self, client, test_product):
        """Teste: Obter um produto por ID"""
        response = client.get(f"/products/{test_product.id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_product.id
        assert data["name"] == test_product.name
        assert data["price"] == test_product.price

    def test_get_product_not_found(self, client):
        """Teste: Obter produto que não existe"""
        response = client.get("/products/9999")
        assert response.status_code == 404
        assert "não encontrado" in response.json()["detail"]


# ============================================================================
# TESTES DE ATUALIZAÇÃO DE PRODUTO
# ============================================================================

class TestProductUpdate:
    """Testes para atualização de produtos"""

    def test_update_product_as_admin(self, client, admin_token, test_product):
        """Teste: Atualizar produto como admin"""
        response = client.put(
            f"/products/{test_product.id}",
            json={
                "name": "Updated Product",
                "price": 149.99,
            },
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 149.99

    def test_update_product_without_auth(self, client, test_product):
        """Teste: Atualizar produto sem autenticação"""
        response = client.put(
            f"/products/{test_product.id}",
            json={"name": "Updated Product"},
        )
        assert response.status_code == 403

    def test_update_product_as_regular_user(self, client, user_token, test_product):
        """Teste: Atualizar produto como usuário regular (deve falhar)"""
        response = client.put(
            f"/products/{test_product.id}",
            json={"name": "Updated Product"},
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403

    def test_update_product_not_found(self, client, admin_token):
        """Teste: Atualizar produto que não existe"""
        response = client.put(
            "/products/9999",
            json={"name": "Updated Product"},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_update_product_invalid_category(self, client, admin_token, test_product):
        """Teste: Atualizar produto com categoria inválida"""
        response = client.put(
            f"/products/{test_product.id}",
            json={"category_id": 9999},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_update_product_invalid_price(self, client, admin_token, test_product):
        """Teste: Atualizar produto com preço inválido"""
        response = client.put(
            f"/products/{test_product.id}",
            json={"price": -10.00},
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 422


# ============================================================================
# TESTES DE DELEÇÃO DE PRODUTO
# ============================================================================

class TestProductDeletion:
    """Testes para deleção de produtos"""

    def test_delete_product_as_admin(self, client, admin_token, test_product):
        """Teste: Deletar produto como admin"""
        response = client.delete(
            f"/products/{test_product.id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204

    def test_delete_product_without_auth(self, client, test_product):
        """Teste: Deletar produto sem autenticação"""
        response = client.delete(f"/products/{test_product.id}")
        assert response.status_code == 403

    def test_delete_product_as_regular_user(self, client, user_token, test_product):
        """Teste: Deletar produto como usuário regular (deve falhar)"""
        response = client.delete(
            f"/products/{test_product.id}",
            headers={"Authorization": f"Bearer {user_token}"},
        )
        assert response.status_code == 403

    def test_delete_product_not_found(self, client, admin_token):
        """Teste: Deletar produto que não existe"""
        response = client.delete(
            "/products/9999",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 404

    def test_delete_product_verify_deletion(self, client, admin_token, test_product):
        """Teste: Verificar se produto foi deletado"""
        product_id = test_product.id
        
        # Deletar produto
        response = client.delete(
            f"/products/{product_id}",
            headers={"Authorization": f"Bearer {admin_token}"},
        )
        assert response.status_code == 204
        
        # Verificar se foi deletado
        response = client.get(f"/products/{product_id}")
        assert response.status_code == 404