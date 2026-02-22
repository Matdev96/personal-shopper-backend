import pytest
from pydantic import ValidationError
from app.schemas.cart import (
    CartItemCreate,
    CartItemUpdate,
)


class TestCartItemCreateSchema:
    """Testes para schema CartItemCreate."""
    
    def test_valid_cart_item_creation(self):
        """Testar criação válida de item do carrinho."""
        item_data = {
            "product_id": 1,
            "quantity": 3,
        }
        item = CartItemCreate(**item_data)
        assert item.product_id == 1
        assert item.quantity == 3
    
    def test_cart_item_product_id_invalid(self):
        """Testar ID do produto inválido."""
        item_data = {
            "product_id": 0,  # ID inválido
            "quantity": 3,
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "product_id" in str(exc_info.value).lower()
    
    def test_cart_item_product_id_negative(self):
        """Testar ID do produto negativo."""
        item_data = {
            "product_id": -1,  # ID negativo
            "quantity": 3,
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "product_id" in str(exc_info.value).lower()
    
    def test_cart_item_quantity_zero(self):
        """Testar quantidade zero."""
        item_data = {
            "product_id": 1,
            "quantity": 0,  # Quantidade zero
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_quantity_negative(self):
        """Testar quantidade negativa."""
        item_data = {
            "product_id": 1,
            "quantity": -5,  # Quantidade negativa
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_quantity_too_large(self):
        """Testar quantidade muito grande."""
        item_data = {
            "product_id": 1,
            "quantity": 1001,  # Mais de 1000
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_quantity_max_valid(self):
        """Testar quantidade máxima válida."""
        item_data = {
            "product_id": 1,
            "quantity": 1000,  # Máximo válido
        }
        item = CartItemCreate(**item_data)
        assert item.quantity == 1000
    
    def test_cart_item_quantity_min_valid(self):
        """Testar quantidade mínima válida."""
        item_data = {
            "product_id": 1,
            "quantity": 1,  # Mínimo válido
        }
        item = CartItemCreate(**item_data)
        assert item.quantity == 1


class TestCartItemUpdateSchema:
    """Testes para schema CartItemUpdate."""
    
    def test_valid_cart_item_update(self):
        """Testar atualização válida de item do carrinho."""
        update_data = {
            "quantity": 5,
        }
        update = CartItemUpdate(**update_data)
        assert update.quantity == 5
    
    def test_cart_item_update_quantity_zero(self):
        """Testar atualização com quantidade zero."""
        update_data = {
            "quantity": 0,  # Quantidade zero
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemUpdate(**update_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_update_quantity_negative(self):
        """Testar atualização com quantidade negativa."""
        update_data = {
            "quantity": -3,  # Quantidade negativa
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemUpdate(**update_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_update_quantity_too_large(self):
        """Testar atualização com quantidade muito grande."""
        update_data = {
            "quantity": 1001,  # Mais de 1000
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemUpdate(**update_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_update_quantity_max_valid(self):
        """Testar atualização com quantidade máxima válida."""
        update_data = {
            "quantity": 1000,  # Máximo válido
        }
        update = CartItemUpdate(**update_data)
        assert update.quantity == 1000
    
    def test_cart_item_update_quantity_min_valid(self):
        """Testar atualização com quantidade mínima válida."""
        update_data = {
            "quantity": 1,  # Mínimo válido
        }
        update = CartItemUpdate(**update_data)
        assert update.quantity == 1
    
    def test_cart_item_update_various_quantities(self):
        """Testar atualização com várias quantidades válidas."""
        valid_quantities = [1, 10, 50, 100, 500, 1000]
        
        for qty in valid_quantities:
            update_data = {"quantity": qty}
            update = CartItemUpdate(**update_data)
            assert update.quantity == qty


class TestCartItemValidation:
    """Testes gerais de validação de itens do carrinho."""
    
    def test_cart_item_create_missing_product_id(self):
        """Testar criação sem product_id."""
        item_data = {
            "quantity": 3,
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "product_id" in str(exc_info.value).lower()
    
    def test_cart_item_create_missing_quantity(self):
        """Testar criação sem quantity."""
        item_data = {
            "product_id": 1,
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_update_missing_quantity(self):
        """Testar atualização sem quantity."""
        update_data = {}
        with pytest.raises(ValidationError) as exc_info:
            CartItemUpdate(**update_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_quantity_not_integer(self):
        """Testar quantidade que não é inteiro."""
        item_data = {
            "product_id": 1,
            "quantity": 3.5,  # Não é inteiro
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_cart_item_product_id_not_integer(self):
        """Testar product_id que não é inteiro."""
        item_data = {
            "product_id": 1.5,  # Não é inteiro
            "quantity": 3,
        }
        with pytest.raises(ValidationError) as exc_info:
            CartItemCreate(**item_data)
        assert "product_id" in str(exc_info.value).lower()