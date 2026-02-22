import pytest
from pydantic import ValidationError
from app.schemas.product import (
    ProductCreate,
    ProductUpdate,
    ProductFilterParams,
)


class TestProductCreateSchema:
    """Testes para schema ProductCreate."""
    
    def test_valid_product_creation(self):
        """Testar criação válida de produto."""
        product_data = {
            "name": "Test Product",
            "description": "This is a test product with detailed description",
            "price": 99.99,
            "category_id": 1,
            "stock": 50,
        }
        product = ProductCreate(**product_data)
        assert product.name == "Test Product"
        assert product.price == 99.99
        assert product.stock == 50
    
    def test_product_name_too_short(self):
        """Testar nome do produto muito curto."""
        product_data = {
            "name": "AB",  # Menos de 3 caracteres
            "description": "This is a test product with detailed description",
            "price": 99.99,
            "category_id": 1,
            "stock": 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "name" in str(exc_info.value).lower()
    
    def test_product_name_too_long(self):
        """Testar nome do produto muito longo."""
        product_data = {
            "name": "A" * 201,  # Mais de 200 caracteres
            "description": "This is a test product with detailed description",
            "price": 99.99,
            "category_id": 1,
            "stock": 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "name" in str(exc_info.value).lower()
    
    def test_product_description_too_short(self):
        """Testar descrição do produto muito curta."""
        product_data = {
            "name": "Test Product",
            "description": "Short",  # Menos de 10 caracteres
            "price": 99.99,
            "category_id": 1,
            "stock": 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "description" in str(exc_info.value).lower()
    
    def test_product_price_negative(self):
        """Testar preço negativo."""
        product_data = {
            "name": "Test Product",
            "description": "This is a test product with detailed description",
            "price": -50.00,  # Preço negativo
            "category_id": 1,
            "stock": 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "price" in str(exc_info.value).lower()
    
    def test_product_price_zero(self):
        """Testar preço zero."""
        product_data = {
            "name": "Test Product",
            "description": "This is a test product with detailed description",
            "price": 0.00,  # Preço zero
            "category_id": 1,
            "stock": 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "price" in str(exc_info.value).lower()
    
    def test_product_price_with_many_decimals(self):
        """Testar preço com muitas casas decimais."""
        product_data = {
            "name": "Test Product",
            "description": "This is a test product with detailed description",
            "price": 99.999,  # Mais de 2 casas decimais
            "category_id": 1,
            "stock": 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "price" in str(exc_info.value).lower()
    
    def test_product_stock_negative(self):
        """Testar estoque negativo."""
        product_data = {
            "name": "Test Product",
            "description": "This is a test product with detailed description",
            "price": 99.99,
            "category_id": 1,
            "stock": -10,  # Estoque negativo
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "stock" in str(exc_info.value).lower()
    
    def test_product_category_id_invalid(self):
        """Testar ID de categoria inválido."""
        product_data = {
            "name": "Test Product",
            "description": "This is a test product with detailed description",
            "price": 99.99,
            "category_id": 0,  # ID inválido
            "stock": 50,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductCreate(**product_data)
        assert "category_id" in str(exc_info.value).lower()
    
    def test_product_with_optional_fields(self):
        """Testar produto com campos opcionais."""
        product_data = {
            "name": "Test Product",
            "description": "This is a test product with detailed description",
            "price": 99.99,
            "category_id": 1,
            "stock": 50,
            "size": "M",
            "color": "Blue",
            "image_url": "https://example.com/image.jpg",
        }
        product = ProductCreate(**product_data)
        assert product.size == "M"
        assert product.color == "Blue"
        assert product.image_url == "https://example.com/image.jpg"


class TestProductUpdateSchema:
    """Testes para schema ProductUpdate."""
    
    def test_valid_update_price(self):
        """Testar atualização válida de preço."""
        update_data = {
            "price": 149.99,
        }
        update = ProductUpdate(**update_data)
        assert update.price == 149.99
    
    def test_valid_update_stock(self):
        """Testar atualização válida de estoque."""
        update_data = {
            "stock": 100,
        }
        update = ProductUpdate(**update_data)
        assert update.stock == 100
    
    def test_update_empty(self):
        """Testar atualização vazia."""
        update_data = {}
        update = ProductUpdate(**update_data)
        assert update.name is None
        assert update.price is None
        assert update.stock is None
    
    def test_update_is_active(self):
        """Testar atualização de status ativo."""
        update_data = {
            "is_active": False,
        }
        update = ProductUpdate(**update_data)
        assert update.is_active is False


class TestProductFilterParamsSchema:
    """Testes para schema ProductFilterParams."""
    
    def test_valid_filter_params(self):
        """Testar parâmetros de filtro válidos."""
        filter_data = {
            "skip": 0,
            "limit": 10,
            "category_id": 1,
            "min_price": 50.00,
            "max_price": 200.00,
            "in_stock": True,
            "search": "camiseta",
            "sort_by": "price",
            "sort_order": "asc",
        }
        filters = ProductFilterParams(**filter_data)
        assert filters.skip == 0
        assert filters.limit == 10
        assert filters.category_id == 1
    
    def test_filter_skip_negative(self):
        """Testar skip negativo."""
        filter_data = {
            "skip": -1,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductFilterParams(**filter_data)
        assert "skip" in str(exc_info.value).lower()
    
    def test_filter_limit_too_small(self):
        """Testar limit menor que 1."""
        filter_data = {
            "limit": 0,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductFilterParams(**filter_data)
        assert "limit" in str(exc_info.value).lower()
    
    def test_filter_limit_too_large(self):
        """Testar limit maior que 100."""
        filter_data = {
            "limit": 101,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductFilterParams(**filter_data)
        assert "limit" in str(exc_info.value).lower()
    
    def test_filter_min_price_negative(self):
        """Testar preço mínimo negativo."""
        filter_data = {
            "min_price": -50.00,
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductFilterParams(**filter_data)
        assert "min_price" in str(exc_info.value).lower()
    
    def test_filter_sort_by_invalid(self):
        """Testar campo de ordenação inválido."""
        filter_data = {
            "sort_by": "invalid_field",
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductFilterParams(**filter_data)
        assert "sort_by" in str(exc_info.value).lower()
    
    def test_filter_sort_order_invalid(self):
        """Testar ordem de classificação inválida."""
        filter_data = {
            "sort_order": "invalid",
        }
        with pytest.raises(ValidationError) as exc_info:
            ProductFilterParams(**filter_data)
        assert "sort_order" in str(exc_info.value).lower()
    
    def test_filter_defaults(self):
        """Testar valores padrão dos filtros."""
        filter_data = {}
        filters = ProductFilterParams(**filter_data)
        assert filters.skip == 0
        assert filters.limit == 10
        assert filters.sort_by == "created_at"
        assert filters.sort_order == "desc"