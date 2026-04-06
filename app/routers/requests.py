from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.dependencies import get_db, get_current_user
from app.models.user import User
from app.models.product_request import ProductRequest, RequestStatus, CLIENTE_PODE_CANCELAR, CLIENTE_PODE_CONFIRMAR
from app.schemas.product_request import (
    ProductRequestCreate,
    ProductRequestResponse,
    ProductRequestListResponse,
)

router = APIRouter(prefix="/requests", tags=["Solicitações"])

MAX_OPEN_REQUESTS = 10


@router.post("", response_model=ProductRequestResponse, status_code=status.HTTP_201_CREATED)
def create_request(
    data: ProductRequestCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Criar uma nova solicitação de busca de produto."""
    open_statuses = [
        s.value for s in RequestStatus
        if s not in {RequestStatus.ENTREGUE, RequestStatus.CANCELADO, RequestStatus.NAO_ENCONTRADO}
    ]
    open_count = (
        db.query(ProductRequest)
        .filter(
            ProductRequest.user_id == current_user.id,
            ProductRequest.status.in_(open_statuses),
        )
        .count()
    )

    if open_count >= MAX_OPEN_REQUESTS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Limite de {MAX_OPEN_REQUESTS} solicitações abertas atingido.",
        )

    request = ProductRequest(
        user_id=current_user.id,
        title=data.title,
        description=data.description,
        reference_image_url=data.reference_image_url,
        preferred_store=data.preferred_store,
        size=data.size,
        color=data.color,
        max_budget=data.max_budget,
        quantity=data.quantity,
        notes=data.notes,
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


@router.get("", response_model=ProductRequestListResponse)
def list_my_requests(
    skip: int = 0,
    limit: int = 10,
    status_filter: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Listar todas as solicitações do usuário logado."""
    query = db.query(ProductRequest).filter(ProductRequest.user_id == current_user.id)

    if status_filter:
        query = query.filter(ProductRequest.status == status_filter)

    total = query.count()
    items = query.order_by(ProductRequest.created_at.desc()).offset(skip).limit(limit).all()
    page = (skip // limit) + 1 if limit > 0 else 1
    pages = (total + limit - 1) // limit if limit > 0 else 1

    return ProductRequestListResponse(items=items, total=total, page=page, pages=pages)


@router.get("/{request_id}", response_model=ProductRequestResponse)
def get_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Detalhe de uma solicitação do usuário logado."""
    req = db.query(ProductRequest).filter(
        ProductRequest.id == request_id,
        ProductRequest.user_id == current_user.id,
    ).first()

    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    return req


@router.put("/{request_id}/confirm", response_model=ProductRequestResponse)
def confirm_quoted_price(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cliente confirma o preço cotado pela Claudia e avança para aguardar sinal."""
    req = db.query(ProductRequest).filter(
        ProductRequest.id == request_id,
        ProductRequest.user_id == current_user.id,
    ).first()

    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    if req.status != RequestStatus.AGUARDANDO_CONFIRMACAO.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Só é possível confirmar quando o status é '{RequestStatus.AGUARDANDO_CONFIRMACAO.value}'.",
        )

    if not req.quoted_price:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A Claudia ainda não informou o preço cotado.",
        )

    req.status = RequestStatus.AGUARDANDO_SINAL.value
    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}/accept-alternative", response_model=ProductRequestResponse)
def accept_alternative(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cliente aceita a alternativa sugerida pela Claudia e avança para aguardar confirmação de preço."""
    req = db.query(ProductRequest).filter(
        ProductRequest.id == request_id,
        ProductRequest.user_id == current_user.id,
    ).first()

    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    if req.status != RequestStatus.ALTERNATIVA_DISPONIVEL.value:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Só é possível aceitar uma alternativa quando o status é 'alternativa_disponivel'.",
        )

    req.status = RequestStatus.AGUARDANDO_CONFIRMACAO.value
    db.commit()
    db.refresh(req)
    return req


@router.put("/{request_id}/cancel", response_model=ProductRequestResponse)
def cancel_request(
    request_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """Cliente cancela uma solicitação (permitido apenas em pendente ou em_busca)."""
    req = db.query(ProductRequest).filter(
        ProductRequest.id == request_id,
        ProductRequest.user_id == current_user.id,
    ).first()

    if not req:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Solicitação não encontrada.")

    if req.status not in [s.value for s in CLIENTE_PODE_CANCELAR]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cancelamento não permitido neste status. Entre em contato com a Claudia.",
        )

    req.status = RequestStatus.CANCELADO.value
    db.commit()
    db.refresh(req)
    return req
