from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from typing import Optional

class ProductBase(BaseModel):
    """Schema base para Product com campos comuns."""
    name: str = Field(..., min_length=1, max_length=255, description="Nome do produto")
    description: Optional[str] = Field(None, max_length=1000, description="Descrição do produto")
    price: float = Field(..., gt=0, description="Preço do produto em USD")
    size: Optional[str] = Field(None, max_length=50, description="Tamanho do produto")
    color: Optional[str] = Field(None, max_length=100, description="Cor do produto")
    category_id: int = Field(..., description="ID da categoria")
    image_url: Optional[str] = Field(None, max_length=500, description="URL da imagem do produto")
    stock: int = Field(default=0, ge=0, description="Quantidade em estoque")


class ProductCreate(ProductBase):
    """Schema para criar um novo produto."""
    pass


class ProductUpdate(BaseModel):
    """Schema para atualizar um produto."""
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = Field(None, max_length=1000)
    price: Optional[float] = Field(None, gt=0)
    size: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=100)
    category_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None
    
class ProductResponse(ProductBase):
    """Schema para resposta de um produto."""
    id: int
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

class ProductUpload(BaseModel):
    """Schema para upload de imagem de produto."""
    product_id: int = Field(..., description="ID do produto")

class ProductFilterParams(BaseModel):
    """Schema para parâmetros de filtro de produtos."""
    skip: int = 0
    limit: int = 10
    category_id: Optional[int] = None
    min_price: Optional[float] = None
    max_price: Optional[float] = None
    in_stock: Optional[bool] = None
    search: Optional[str] = None
    sort_by: Optional[str] = "created_at"  # created_at, price, name
    sort_order: Optional[str] = "desc"  # asc, desc
    
    class Config:
        from_attributes = True