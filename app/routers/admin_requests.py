from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.dependencies import get_db, get_current_admin_user
from app.models.user import User
from app.models.product_request import ProductRequest, RequestStatus, ADMIN_TRANSICOES
from app.models.payment import Payment, PaymentStatus
from app.schemas.product_request import (
    AdminUpdateStatus,
    AdminQuotePrice,
    AdminSuggestAlternative,
    AdminRequestResponse,
    AdminRequestListResponse,
)
from app.schemas.payment import PaymentResponse, AdminReviewPayment

router = APIRouter(prefix="/admin/requests", tags=["Admin — Solicitações"])


@router.get("", response_model=AdminRequestListResponse)
def list_all_requests(
    skip: int = 0,
    limit: int = 10,
    status_filter: Optional[str] = Query(None),
    user_id: Optional[int] = Query(None),
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Lista todas as solicitações com filtros opcionais."""
    query = db.query(ProductRequest)

    if status_filter:
        query = query.filter(ProductRequest.status == status_filter)
    if user_id:
        query = query.filter(ProductRequest.user_id == user_id)

    total = query.count()
    items = query.order_by(ProductRequest.created_at.desc()).offset(skip).limit(limit).all()
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1

    return AdminRequestListResponse(items=items, total=total, page=page, pages=pages)


@router.get("/{request_id}", response_model=AdminRequestResponse)
def get_request(
    request_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Detalhe de qualquer solicitação."""
    req = db.query(ProductRequest).filter(ProductRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")
    return req


@router.put("/{request_id}/status", response_model=AdminRequestResponse)
def update_status(
    request_id: int,
    data: AdminUpdateStatus,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Admin atualiza o status de uma solicitação.
    Segue as transições permitidas definidas em ADMIN_TRANSICOES.
    """
    req = db.query(ProductRequest).filter(ProductRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    current = RequestStatus(req.status)
    allowed_next = ADMIN_TRANSICOES.get(current)

    if allowed_next is None or data.status != allowed_next:
        allowed_label = allowed_next.value if allowed_next else "nenhum"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Transição inválida: '{current.value}' → '{data.status.value}'. Próximo permitido: '{allowed_label}'.",
        )

    req.status = data.status.value
    if data.admin_notes:
        req.admin_notes = data.admin_notes

    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}/quote", response_model=AdminRequestResponse)
def quote_price(
    request_id: int,
    data: AdminQuotePrice,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Admin registra o preço cotado e avança para 'aguardando_confirmacao'.
    Permitido somente quando status == 'encontrado'.
    """
    req = db.query(ProductRequest).filter(ProductRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    if req.status != RequestStatus.ENCONTRADO.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Preço só pode ser cotado quando o status é 'encontrado'.",
        )

    req.quoted_price = data.quoted_price
    req.found_image_url = data.found_image_url
    req.admin_notes = data.admin_notes
    req.status = RequestStatus.AGUARDANDO_CONFIRMACAO.value

    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}/suggest-alternative", response_model=AdminRequestResponse)
def suggest_alternative(
    request_id: int,
    data: AdminSuggestAlternative,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Admin sugere uma alternativa quando o produto exato não foi encontrado.
    Permitido nos status 'em_busca' e 'encontrado'.
    O cliente poderá aceitar a alternativa ou cancelar a solicitação.
    """
    req = db.query(ProductRequest).filter(ProductRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    if req.status not in [RequestStatus.EM_BUSCA.value, RequestStatus.ENCONTRADO.value]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Alternativa só pode ser sugerida nos status 'em_busca' ou 'encontrado'.",
        )

    req.quoted_price = data.quoted_price
    req.found_image_url = data.found_image_url
    req.admin_notes = data.alternative_description
    req.status = RequestStatus.ALTERNATIVA_DISPONIVEL.value

    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}/cancel", response_model=AdminRequestResponse)
def admin_cancel_request(
    request_id: int,
    data: AdminUpdateStatus,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Admin pode cancelar qualquer solicitação, exceto as já entregues."""
    req = db.query(ProductRequest).filter(ProductRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    if req.status == RequestStatus.ENTREGUE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível cancelar uma solicitação já entregue.",
        )

    req.status = RequestStatus.CANCELADO.value
    if data.admin_notes:
        req.admin_notes = data.admin_notes

    db.commit()
    db.refresh(req)
    return req


# ---------------------------------------------------------------------------
# Revisão de pagamentos
# ---------------------------------------------------------------------------

@router.get("/{request_id}/payments", response_model=List[PaymentResponse])
def list_payments(
    request_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Lista os pagamentos de uma solicitação."""
    req = db.query(ProductRequest).filter(ProductRequest.id == request_id).first()
    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")
    return req.payments


@router.put("/{request_id}/payments/{payment_id}/review", response_model=PaymentResponse)
def review_payment(
    request_id: int,
    payment_id: int,
    data: AdminReviewPayment,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Admin confirma ou rejeita um pagamento.
    - Confirmar sinal → avança solicitação para 'sinal_confirmado'
    - Confirmar final → avança para 'entregue'
    - Rejeitar → devolve status anterior para o cliente reenviar
    """
    payment = db.query(Payment).filter(
        Payment.id == payment_id,
        Payment.request_id == request_id,
    ).first()

    if not payment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pagamento não encontrado.")

    if payment.status != PaymentStatus.PENDENTE.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Este pagamento já foi revisado.",
        )

    req = db.query(ProductRequest).filter(ProductRequest.id == request_id).first()

    payment.status = data.status.value
    if data.admin_notes:
        payment.admin_notes = data.admin_notes

    if data.status == PaymentStatus.CONFIRMADO:
        from app.models.payment import PaymentType
        if payment.type == PaymentType.SINAL.value:
            req.status = RequestStatus.SINAL_CONFIRMADO.value
        elif payment.type == PaymentType.FINAL.value:
            req.status = RequestStatus.ENTREGUE.value

    elif data.status == PaymentStatus.REJEITADO:
        from app.models.payment import PaymentType
        if payment.type == PaymentType.SINAL.value:
            req.status = RequestStatus.AGUARDANDO_SINAL.value
        elif payment.type == PaymentType.FINAL.value:
            req.status = RequestStatus.AGUARDANDO_PAGAMENTO_FINAL.value

    db.commit()
    db.refresh(payment)
    return payment
