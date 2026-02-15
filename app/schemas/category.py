# app/schemas/category.py

from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

class CategoryCreate(BaseModel):
    """
    Schema para criar uma nova categoria.
    """
    name: str = Field(..., min_length=1, max_length=100, description="Nome da categoria")
    description: Optional[str] = Field(None, max_length=500, description="Descrição da categoria")

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Eletrônicos",
                "description": "Produtos eletrônicos em geral"
            }
        }


class CategoryResponse(BaseModel):
    """
    Schema para retornar dados da categoria.
    """
    id: int
    name: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "name": "Eletrônicos",
                "description": "Produtos eletrônicos em geral",
                "created_at": "2026-02-15T10:30:00",
                "updated_at": "2026-02-15T10:30:00"
            }
        }


class CategoryUpdate(BaseModel):
    """
    Schema para atualizar uma categoria.
    Todos os campos são opcionais.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=500)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Eletrônicos Novos",
                "description": "Descrição atualizada"
            }
        }