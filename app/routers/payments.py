from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.product_request import ProductRequest, RequestStatus
from app.models.payment import Payment, PaymentType, PaymentStatus
from app.schemas.payment import PaymentCreate, PaymentResponse

router = APIRouter(prefix="/payments", tags=["Pagamentos"])


@router.post("", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
def register_payment(
    data: PaymentCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cliente registra um pagamento (sinal ou final).
    - Sinal: permitido somente quando status == 'aguardando_sinal'
    - Final: permitido somente quando status == 'aguardando_pagamento_final'
    """
    req = db.query(ProductRequest).filter(
        ProductRequest.id == data.request_id,
        ProductRequest.user_id == current_user.id,
    ).first()

    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    # Validar status correto para cada tipo de pagamento
    if data.type == PaymentType.SINAL:
        if req.status != RequestStatus.AGUARDANDO_SINAL.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O sinal só pode ser registrado quando a solicitação está em 'aguardando_sinal'.",
            )
        # Validar valor mínimo do sinal (50% do preço cotado)
        if req.quoted_price and data.amount < round(req.quoted_price * 0.5, 2):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"O sinal mínimo é R$ {req.quoted_price * 0.5:.2f} (50% de R$ {req.quoted_price:.2f}).",
            )
        # Verificar se já existe sinal pendente ou confirmado
        existing = db.query(Payment).filter(
            Payment.request_id == req.id,
            Payment.type == PaymentType.SINAL.value,
            Payment.status != PaymentStatus.REJEITADO.value,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um sinal registrado para esta solicitação.",
            )

    elif data.type == PaymentType.FINAL:
        if req.status != RequestStatus.AGUARDANDO_PAGAMENTO_FINAL.value:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="O pagamento final só pode ser registrado quando a solicitação está em 'aguardando_pagamento_final'.",
            )
        # Verificar se já existe pagamento final pendente ou confirmado
        existing = db.query(Payment).filter(
            Payment.request_id == req.id,
            Payment.type == PaymentType.FINAL.value,
            Payment.status != PaymentStatus.REJEITADO.value,
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Já existe um pagamento final registrado para esta solicitação.",
            )

    payment = Payment(
        request_id=data.request_id,
        user_id=current_user.id,
        type=data.type.value,
        amount=data.amount,
        payment_method=data.payment_method,
        payment_date=data.payment_date,
        receipt_url=data.receipt_url,
        status=PaymentStatus.PENDENTE.value,
    )
    db.add(payment)

    # Avança status da solicitação para indicar que o pagamento foi enviado
    if data.type == PaymentType.SINAL:
        req.status = RequestStatus.SINAL_PAGO.value
    elif data.type == PaymentType.FINAL:
        req.status = RequestStatus.PAGO.value

    db.commit()
    db.refresh(payment)
    return payment


@router.get("/my", response_model=List[PaymentResponse])
def list_my_payments(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Lista todos os pagamentos do usuário logado."""
    payments = (
        db.query(Payment)
        .filter(Payment.user_id == current_user.id)
        .order_by(Payment.created_at.desc())
        .all()
    )
    return payments
