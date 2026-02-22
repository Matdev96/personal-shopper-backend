import pytest
from pydantic import ValidationError
from app.schemas.order import (
    OrderItemCreate,
    OrderCreate,
    OrderStatusUpdate,
    OrderStatusEnum,
)


class TestOrderItemCreateSchema:
    """Testes para schema OrderItemCreate."""
    
    def test_valid_order_item(self):
        """Testar criação válida de item do pedido."""
        item_data = {
            "product_id": 1,
            "quantity": 5,
        }
        item = OrderItemCreate(**item_data)
        assert item.product_id == 1
        assert item.quantity == 5
    
    def test_order_item_product_id_invalid(self):
        """Testar ID do produto inválido."""
        item_data = {
            "product_id": 0,  # ID inválido
            "quantity": 5,
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(**item_data)
        assert "product_id" in str(exc_info.value).lower()
    
    def test_order_item_quantity_zero(self):
        """Testar quantidade zero."""
        item_data = {
            "product_id": 1,
            "quantity": 0,  # Quantidade zero
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(**item_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_order_item_quantity_negative(self):
        """Testar quantidade negativa."""
        item_data = {
            "product_id": 1,
            "quantity": -5,  # Quantidade negativa
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(**item_data)
        assert "quantity" in str(exc_info.value).lower()
    
    def test_order_item_quantity_too_large(self):
        """Testar quantidade muito grande."""
        item_data = {
            "product_id": 1,
            "quantity": 1001,  # Mais de 1000
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderItemCreate(**item_data)
        assert "quantity" in str(exc_info.value).lower()


class TestOrderCreateSchema:
    """Testes para schema OrderCreate."""
    
    def test_valid_order_creation(self):
        """Testar criação válida de pedido."""
        order_data = {
            "items": [
                {"product_id": 1, "quantity": 2},
                {"product_id": 2, "quantity": 3},
            ],
            "shipping_address": "123 Test Street, Test City, Test Country",
            "payment_method": "credit_card",
        }
        order = OrderCreate(**order_data)
        assert len(order.items) == 2
        assert order.shipping_address == "123 Test Street, Test City, Test Country"
        assert order.payment_method == "credit_card"
    
    def test_order_no_items(self):
        """Testar pedido sem itens."""
        order_data = {
            "items": [],  # Sem itens
            "shipping_address": "123 Test Street, Test City, Test Country",
            "payment_method": "credit_card",
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(**order_data)
        assert "items" in str(exc_info.value).lower()
    
    def test_order_too_many_items(self):
        """Testar pedido com muitos itens."""
        items = [{"product_id": i, "quantity": 1} for i in range(101)]
        order_data = {
            "items": items,  # Mais de 100 itens
            "shipping_address": "123 Test Street, Test City, Test Country",
            "payment_method": "credit_card",
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(**order_data)
        assert "items" in str(exc_info.value).lower()
    
    def test_order_shipping_address_too_short(self):
        """Testar endereço de entrega muito curto."""
        order_data = {
            "items": [{"product_id": 1, "quantity": 2}],
            "shipping_address": "Short",  # Menos de 10 caracteres
            "payment_method": "credit_card",
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(**order_data)
        assert "shipping_address" in str(exc_info.value).lower()
    
    def test_order_shipping_address_no_number(self):
        """Testar endereço de entrega sem número."""
        order_data = {
            "items": [{"product_id": 1, "quantity": 2}],
            "shipping_address": "Test Street, Test City, Test Country",  # Sem número
            "payment_method": "credit_card",
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(**order_data)
        assert "shipping_address" in str(exc_info.value).lower()
    
    def test_order_invalid_payment_method(self):
        """Testar método de pagamento inválido."""
        order_data = {
            "items": [{"product_id": 1, "quantity": 2}],
            "shipping_address": "123 Test Street, Test City, Test Country",
            "payment_method": "invalid_method",  # Método inválido
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderCreate(**order_data)
        assert "payment_method" in str(exc_info.value).lower()
    
    def test_order_valid_payment_methods(self):
        """Testar todos os métodos de pagamento válidos."""
        valid_methods = ["credit_card", "debit_card", "pix", "boleto", "paypal"]
        
        for method in valid_methods:
            order_data = {
                "items": [{"product_id": 1, "quantity": 2}],
                "shipping_address": "123 Test Street, Test City, Test Country",
                "payment_method": method,
            }
            order = OrderCreate(**order_data)
            assert order.payment_method == method.lower()
    
    def test_order_payment_method_case_insensitive(self):
        """Testar que método de pagamento é case-insensitive."""
        order_data = {
            "items": [{"product_id": 1, "quantity": 2}],
            "shipping_address": "123 Test Street, Test City, Test Country",
            "payment_method": "CREDIT_CARD",  # Maiúsculas
        }
        order = OrderCreate(**order_data)
        assert order.payment_method == "credit_card"  # Convertido para minúsculas


class TestOrderStatusUpdateSchema:
    """Testes para schema OrderStatusUpdate."""
    
    def test_valid_status_update(self):
        """Testar atualização válida de status."""
        update_data = {
            "new_status": "processing",
        }
        update = OrderStatusUpdate(**update_data)
        assert update.new_status == OrderStatusEnum.PROCESSING
    
    def test_all_valid_statuses(self):
        """Testar todos os status válidos."""
        valid_statuses = ["pending", "processing", "shipped", "delivered", "cancelled"]
        
        for status in valid_statuses:
            update_data = {
                "new_status": status,
            }
            update = OrderStatusUpdate(**update_data)
            assert update.new_status.value == status
    
    def test_invalid_status(self):
        """Testar status inválido."""
        update_data = {
            "new_status": "invalid_status",
        }
        with pytest.raises(ValidationError) as exc_info:
            OrderStatusUpdate(**update_data)
        assert "new_status" in str(exc_info.value).lower()


class TestOrderStatusEnum:
    """Testes para enum OrderStatusEnum."""
    
    def test_status_enum_values(self):
        """Testar valores do enum de status."""
        assert OrderStatusEnum.PENDING.value == "pending"
        assert OrderStatusEnum.PROCESSING.value == "processing"
        assert OrderStatusEnum.SHIPPED.value == "shipped"
        assert OrderStatusEnum.DELIVERED.value == "delivered"
        assert OrderStatusEnum.CANCELLED.value == "cancelled"
    
    def test_status_enum_from_string(self):
        """Testar criação de enum a partir de string."""
        status = OrderStatusEnum("pending")
        assert status == OrderStatusEnum.PENDING
    
    def test_status_enum_comparison(self):
        """Testar comparação de enums."""
        status1 = OrderStatusEnum.PENDING
        status2 = OrderStatusEnum.PENDING
        assert status1 == status2