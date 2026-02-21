from pydantic import BaseModel, Field, validator
from typing import List, Optional
from datetime import datetime
from enum import Enum


class OrderStatusEnum(str, Enum):
    """Enum para status de pedidos."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemBase(BaseModel):
    """Base para item do pedido."""
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


class OrderItemCreate(OrderItemBase):
    """Schema para criar item do pedido."""
    pass


class OrderItemResponse(OrderItemBase):
    """Schema para resposta de item do pedido."""
    id: int
    order_id: int
    price_at_time: float = Field(..., gt=0, description="Preço do produto no momento do pedido")
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema para criar um novo pedido."""
    items: List[OrderItemCreate] = Field(
        ..., 
        min_items=1, 
        max_items=100,
        description="Itens do pedido (mínimo 1, máximo 100)"
    )
    shipping_address: str = Field(
        ..., 
        min_length=10, 
        max_length=500,
        description="Endereço de entrega (mínimo 10 caracteres)"
    )
    payment_method: str = Field(
        ..., 
        min_length=3,
        max_length=50,
        description="Método de pagamento (credit_card, debit_card, pix, etc)"
    )
    
    @validator('shipping_address')
    def validate_shipping_address(cls, v):
        """Validar endereço de entrega."""
        if not any(char.isdigit() for char in v):
            raise ValueError('Endereço deve conter pelo menos um número')
        return v
    
    @validator('payment_method')
    def validate_payment_method(cls, v):
        """Validar método de pagamento."""
        valid_methods = ['credit_card', 'debit_card', 'pix', 'boleto', 'paypal']
        if v.lower() not in valid_methods:
            raise ValueError(f'Método de pagamento deve ser um de: {", ".join(valid_methods)}')
        return v.lower()


class OrderResponse(BaseModel):
    """Schema para resposta de pedido."""
    id: int
    user_id: int
    items: List[OrderItemResponse] = []
    total_price: float = Field(..., ge=0, description="Preço total do pedido")
    shipping_address: str
    payment_method: str
    status: OrderStatusEnum
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class OrderStatusUpdate(BaseModel):
    """Schema para atualizar status do pedido."""
    new_status: OrderStatusEnum = Field(..., description="Novo status do pedido")


class StockValidationRequest(BaseModel):
    """Schema para validação de estoque."""
    items: List[OrderItemCreate] = Field(
        ..., 
        min_items=1,
        description="Itens para validar"
    )


class StockValidationResponse(BaseModel):
    """Schema para resposta de validação de estoque."""
    valid: bool = Field(..., description="Se o estoque é válido")
    message: str = Field(..., description="Mensagem de validação")
    items_status: List[dict] = Field(
        default=[], 
        description="Status de cada item"
    )