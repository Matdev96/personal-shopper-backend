from pydantic import BaseModel, Field, validator
from typing import Optional, List
from datetime import datetime
from app.models.product_request import RequestStatus


class UserInRequest(BaseModel):
    id: int
    full_name: Optional[str]
    email: str

    class Config:
        from_attributes = True


class PaymentInRequest(BaseModel):
    id: int
    type: str
    amount: float
    payment_method: str
    payment_date: datetime
    status: str
    receipt_url: Optional[str] = None

    class Config:
        from_attributes = True


# ---------------------------------------------------------------------------
# Schemas do Cliente
# ---------------------------------------------------------------------------

class ProductRequestCreate(BaseModel):
    title: str = Field(..., min_length=3, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    reference_image_url: Optional[str] = Field(None, max_length=500)
    preferred_store: Optional[str] = Field(None, max_length=200)
    size: Optional[str] = Field(None, max_length=50)
    color: Optional[str] = Field(None, max_length=50)
    max_budget: Optional[float] = Field(None, gt=0)
    quantity: int = Field(1, ge=1, le=50)
    notes: Optional[str] = Field(None, max_length=1000)


class ProductRequestResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: Optional[str]
    reference_image_url: Optional[str]
    preferred_store: Optional[str]
    size: Optional[str]
    color: Optional[str]
    max_budget: Optional[float]
    quantity: int
    notes: Optional[str]
    status: str
    quoted_price: Optional[float]
    found_image_url: Optional[str]
    deposit_amount: float
    remaining_amount: float
    payments: List[PaymentInRequest] = []
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ProductRequestListResponse(BaseModel):
    items: List[ProductRequestResponse]
    total: int
    page: int
    pages: int


# ---------------------------------------------------------------------------
# Schemas do Admin
# ---------------------------------------------------------------------------

class AdminUpdateStatus(BaseModel):
    status: RequestStatus
    admin_notes: Optional[str] = Field(None, max_length=1000)


class AdminQuotePrice(BaseModel):
    quoted_price: float = Field(..., gt=0)
    found_image_url: Optional[str] = Field(None, max_length=500)
    admin_notes: Optional[str] = Field(None, max_length=1000)

    @validator("quoted_price")
    def validate_price(cls, v):
        if round(v, 2) != v:
            raise ValueError("Preço deve ter no máximo 2 casas decimais")
        return v


class AdminRequestResponse(ProductRequestResponse):
    user: Optional[UserInRequest] = None

    class Config:
        from_attributes = True


class AdminRequestListResponse(BaseModel):
    items: List[AdminRequestResponse]
    total: int
    page: int
    pages: int
