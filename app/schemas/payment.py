from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.payment import PaymentType, PaymentStatus

VALID_METHODS = {"pix", "transferencia", "dinheiro", "cartao"}


class PaymentCreate(BaseModel):
    request_id: int = Field(..., gt=0)
    type: PaymentType
    amount: float = Field(..., gt=0)
    payment_method: str = Field(..., min_length=2, max_length=50)
    payment_date: datetime
    receipt_url: Optional[str] = Field(None, max_length=500)

    @validator("payment_method")
    def validate_method(cls, v):
        if v not in VALID_METHODS:
            raise ValueError(f"Método inválido. Use: {', '.join(VALID_METHODS)}")
        return v

    @validator("amount")
    def validate_amount(cls, v):
        if round(v, 2) != v:
            raise ValueError("Valor deve ter no máximo 2 casas decimais")
        return v


class PaymentResponse(BaseModel):
    id: int
    request_id: int
    user_id: int
    type: str
    amount: float
    payment_method: str
    payment_date: datetime
    receipt_url: Optional[str]
    status: str
    admin_notes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class AdminReviewPayment(BaseModel):
    status: PaymentStatus = Field(..., description="confirmado ou rejeitado")
    admin_notes: Optional[str] = Field(None, max_length=500)

    @validator("status")
    def validate_status(cls, v):
        if v == PaymentStatus.PENDENTE:
            raise ValueError("Use 'confirmado' ou 'rejeitado'")
        return v
