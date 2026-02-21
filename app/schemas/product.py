from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class ProductBase(BaseModel):
    """Base para produto."""
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=200,
        description="Nome do produto"
    )
    description: str = Field(
        ..., 
        min_length=10, 
        max_length=2000,
        description="Descrição do produto"
    )
    price: float = Field(
        ..., 
        gt=0,
        description="Preço do produto (deve ser maior que 0)"
    )
    category_id: int = Field(
        ..., 
        gt=0,
        description="ID da categoria"
    )
    stock: int = Field(
        ..., 
        ge=0,
        description="Quantidade em estoque (não pode ser negativa)"
    )
    size: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=50,
        description="Tamanho do produto"
    )
    color: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=50,
        description="Cor do produto"
    )
    image_url: Optional[str] = Field(
        None, 
        max_length=500,
        description="URL da imagem do produto"
    )
    
    @validator('price')
    def validate_price(cls, v):
        """Validar preço com até 2 casas decimais."""
        if round(v, 2) != v:
            raise ValueError('Preço deve ter no máximo 2 casas decimais')
        return v
    
    @validator('stock')
    def validate_stock(cls, v):
        """Validar que estoque é um número inteiro positivo."""
        if not isinstance(v, int):
            raise ValueError('Estoque deve ser um número inteiro')
        return v


class ProductCreate(ProductBase):
    """Schema para criar um novo produto."""
    pass


class ProductUpdate(BaseModel):
    """Schema para atualizar um produto."""
    name: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=200,
        description="Nome do produto"
    )
    description: Optional[str] = Field(
        None, 
        min_length=10, 
        max_length=2000,
        description="Descrição do produto"
    )
    price: Optional[float] = Field(
        None, 
        gt=0,
        description="Preço do produto"
    )
    category_id: Optional[int] = Field(
        None, 
        gt=0,
        description="ID da categoria"
    )
    stock: Optional[int] = Field(
        None, 
        ge=0,
        description="Quantidade em estoque"
    )
    size: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=50,
        description="Tamanho do produto"
    )
    color: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=50,
        description="Cor do produto"
    )
    image_url: Optional[str] = Field(
        None, 
        max_length=500,
        description="URL da imagem do produto"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Se o produto está ativo"
    )
    
    @validator('price')
    def validate_price(cls, v):
        """Validar preço com até 2 casas decimais."""
        if v is None:
            return v
        if round(v, 2) != v:
            raise ValueError('Preço deve ter no máximo 2 casas decimais')
        return v
    
    @validator('stock')
    def validate_stock(cls, v):
        """Validar que estoque é um número inteiro positivo."""
        if v is None:
            return v
        if not isinstance(v, int):
            raise ValueError('Estoque deve ser um número inteiro')
        return v


class ProductResponse(BaseModel):
    """Schema para resposta de produto."""
    id: int
    name: str
    description: str
    price: float
    size: Optional[str]
    color: Optional[str]
    category_id: int
    image_url: Optional[str]
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class ProductFilterParams(BaseModel):
    """Schema para parâmetros de filtro de produtos."""
    skip: int = 0
    limit: int = 10
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    search: Optional[str] = None
    sort_by: Optional[str] = "created_at"
    sort_order: Optional[str] = "desc"
    
    @validator('skip')
    def validate_skip(cls, v):
        """Validar skip."""
        if v < 0:
            raise ValueError('skip não pode ser negativo')
        return v
    
    @validator('limit')
    def validate_limit(cls, v):
        """Validar limit."""
        if v < 1 or v > 100:
            raise ValueError('limit deve estar entre 1 e 100')
        return v
    
    @validator('min_price')
    def validate_min_price(cls, v):
        """Validar preço mínimo."""
        if v is not None and v < 0:
            raise ValueError('min_price não pode ser negativo')
        return v
    
    @validator('max_price')
    def validate_max_price(cls, v):
        """Validar preço máximo."""
        if v is not None and v < 0:
            raise ValueError('max_price não pode ser negativo')
        return v
    
    @validator('sort_by')
    def validate_sort_by(cls, v):
        """Validar campo de ordenação."""
        valid_fields = ['created_at', 'price', 'name']
        if v not in valid_fields:
            raise ValueError(f'sort_by deve ser um de: {", ".join(valid_fields)}')
        return v
    
    @validator('sort_order')
    def validate_sort_order(cls, v):
        """Validar ordem de classificação."""
        if v not in ['asc', 'desc']:
            raise ValueError('sort_order deve ser "asc" ou "desc"')
        return v
    
    class Config:
        from_attributes = True