from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class OrderStatusEnum(str, Enum):
    """Enum para status de pedidos."""
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItemCreate(BaseModel):
    """Schema para criar item do pedido."""
    product_id: int = Field(..., description="ID do produto")
    quantity: int = Field(..., gt=0, description="Quantidade")
    price: float = Field(..., gt=0, description="Preço unitário")


class OrderItemResponse(BaseModel):
    """Schema para resposta de item do pedido."""
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    subtotal: float = Field(..., description="Quantidade × Preço")
    
    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    """Schema para criar um pedido."""
    items: list[OrderItemCreate] = Field(..., min_items=1, description="Itens do pedido")
    shipping_address: str = Field(..., min_length=10, max_length=500, description="Endereço de entrega")
    payment_method: str = Field(..., description="Método de pagamento (credit_card, debit_card, paypal)")


class OrderResponse(BaseModel):
    """Schema para resposta de um pedido."""
    id: int
    user_id: int
    items: list[OrderItemResponse] = Field(default_factory=list)
    total_price: float = Field(..., description="Preço total do pedido")
    status: str = Field(..., description="Status do pedido (pending, confirmed, shipped, delivered, cancelled)")
    shipping_address: str
    payment_method: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True


class StockValidationRequest(BaseModel):
    """Schema para validar estoque."""
    items: list[OrderItemCreate] = Field(..., min_items=1, description="Itens para validar")


class StockValidationResponse(BaseModel):
    """Schema para resposta de validação de estoque."""
    is_valid: bool = Field(..., description="Se todos os itens têm estoque")
    message: str = Field(..., description="Mensagem de validação")
    unavailable_items: list[dict] = Field(default_factory=list, description="Itens sem estoque")
    
    class Config:
        from_attributes = True
