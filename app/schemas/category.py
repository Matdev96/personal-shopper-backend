from pydantic import BaseModel, Field, validator
from typing import Optional
from datetime import datetime


class CategoryBase(BaseModel):
    """Base para categoria."""
    name: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Nome da categoria"
    )
    description: Optional[str] = Field(
        None, 
        min_length=10, 
        max_length=500,
        description="Descrição da categoria"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validar nome da categoria."""
        if not v.strip():
            raise ValueError('Nome da categoria não pode estar vazio')
        if any(char in v for char in ['<', '>', '{', '}', '|']):
            raise ValueError('Nome da categoria contém caracteres inválidos')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validar descrição da categoria."""
        if v is not None and not v.strip():
            raise ValueError('Descrição não pode estar vazia')
        return v.strip() if v else None


class CategoryCreate(CategoryBase):
    """Schema para criar uma nova categoria."""
    pass


class CategoryUpdate(BaseModel):
    """Schema para atualizar uma categoria."""
    name: Optional[str] = Field(
        None, 
        min_length=3, 
        max_length=100,
        description="Nome da categoria"
    )
    description: Optional[str] = Field(
        None, 
        min_length=10, 
        max_length=500,
        description="Descrição da categoria"
    )
    is_active: Optional[bool] = Field(
        None,
        description="Se a categoria está ativa"
    )
    
    @validator('name')
    def validate_name(cls, v):
        """Validar nome da categoria."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Nome da categoria não pode estar vazio')
        if any(char in v for char in ['<', '>', '{', '}', '|']):
            raise ValueError('Nome da categoria contém caracteres inválidos')
        return v.strip()
    
    @validator('description')
    def validate_description(cls, v):
        """Validar descrição da categoria."""
        if v is None:
            return v
        if not v.strip():
            raise ValueError('Descrição não pode estar vazia')
        return v.strip()


class CategoryResponse(BaseModel):
    """Schema para resposta de categoria."""
    id: int
    name: str
    description: Optional[str]
    is_active: bool
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True