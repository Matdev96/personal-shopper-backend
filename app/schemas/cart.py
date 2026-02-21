from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime


class CartItemBase(BaseModel):
    """Base para item do carrinho."""
    product_id: int = Field(..., gt=0, description="ID do produto")
    quantity: int = Field(..., gt=0, description="Quantidade do item")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Validar que quantidade é um número inteiro positivo."""
        if not isinstance(v, int):
            raise ValueError('Quantidade deve ser um número inteiro')
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que 0')
        if v > 1000:
            raise ValueError('Quantidade não pode exceder 1000 unidades')
        return v


class CartItemCreate(CartItemBase):
    """Schema para criar item do carrinho."""
    pass


class CartItemResponse(CartItemBase):
    """Schema para resposta de item do carrinho."""
    id: int
    cart_id: int
    price_at_time: float = Field(..., gt=0, description="Preço do produto no momento da adição")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class CartResponse(BaseModel):
    """Schema para resposta do carrinho."""
    id: int
    user_id: int
    items: List[CartItemResponse] = []
    created_at: datetime
    updated_at: datetime
    
    @property
    def total_items(self) -> int:
        """Calcular total de itens no carrinho."""
        return sum(item.quantity for item in self.items)
    
    @property
    def total_price(self) -> float:
        """Calcular preço total do carrinho."""
        return sum(item.price_at_time * item.quantity for item in self.items)
    
    class Config:
        from_attributes = True


class CartItemUpdate(BaseModel):
    """Schema para atualizar item do carrinho."""
    quantity: int = Field(..., gt=0, description="Nova quantidade")
    
    @validator('quantity')
    def validate_quantity(cls, v):
        """Validar que quantidade é um número inteiro positivo."""
        if not isinstance(v, int):
            raise ValueError('Quantidade deve ser um número inteiro')
        if v <= 0:
            raise ValueError('Quantidade deve ser maior que 0')
        if v > 1000:
            raise ValueError('Quantidade não pode exceder 1000 unidades')
        return v