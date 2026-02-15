# app/schemas/product.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class ProductCreate(BaseModel):
    """
    Schema para criar um novo produto.
    """
    name: str = Field(..., min_length=1, max_length=255, description="Nome do produto")
    description: Optional[str] = Field(None, description="Descrição do produto")
    price: float = Field(..., gt=0, description="Preço do produto (maior que 0)")
    category_id: int = Field(..., description="ID da categoria")
    image_url: Optional[str] = Field(None, max_length=500, description="URL da imagem")
    stock: int = Field(default=0, ge=0, description="Quantidade em estoque")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "iPhone 15",
                "description": "Smartphone Apple última geração",
                "price": 999.99,
                "category_id": 1,
                "image_url": "https://example.com/iphone15.jpg",
                "stock": 50
            }
        }


class ProductResponse(BaseModel):
    """
    Schema para retornar dados do produto.
    """
    id: int
    name: str
    description: Optional[str]
    price: float
    category_id: int
    image_url: Optional[str]
    stock: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "iPhone 15",
                "description": "Smartphone Apple última geração",
                "price": 999.99,
                "category_id": 1,
                "image_url": "https://example.com/iphone15.jpg",
                "stock": 50,
                "is_active": True,
                "created_at": "2026-02-15T10:30:00",
                "updated_at": "2026-02-15T10:30:00"
            }
        }


class ProductUpdate(BaseModel):
    """
    Schema para atualizar um produto.
    Todos os campos são opcionais.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    price: Optional[float] = Field(None, gt=0)
    category_id: Optional[int] = None
    image_url: Optional[str] = Field(None, max_length=500)
    stock: Optional[int] = Field(None, ge=0)
    is_active: Optional[bool] = None

    class Config:
        json_schema_extra = {
            "example": {
                "price": 899.99,
                "stock": 45
            }
        }


class ProductFilter(BaseModel):
    """
    Schema para filtrar produtos.
    Usado em query parameters.
    """
    category_id: Optional[int] = Field(None, description="Filtrar por categoria")
    min_price: Optional[float] = Field(None, ge=0, description="Preço mínimo")
    max_price: Optional[float] = Field(None, ge=0, description="Preço máximo")
    search: Optional[str] = Field(None, max_length=255, description="Buscar por nome")
    is_active: Optional[bool] = Field(None, description="Apenas produtos ativos")
    skip: int = Field(default=0, ge=0, description="Paginação - quantos pular")
    limit: int = Field(default=10, ge=1, le=100, description="Paginação - quantos retornar")

    class Config:
        json_schema_extra = {
            "example": {
                "category_id": 1,
                "min_price": 100.0,
                "max_price": 1000.0,
                "search": "iPhone",
                "is_active": True,
                "skip": 0,
                "limit": 10
            }
        }