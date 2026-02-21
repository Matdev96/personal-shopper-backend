from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.order import (
    StockValidationRequest,
    StockValidationResponse,
    OrderCreate,
    OrderResponse,
)
from app.models.product import Product
from app.models.order import Order, OrderItem
from app.models.user import User
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/stock", tags=["Stock"])


@router.post("/validate", response_model=StockValidationResponse)
def validate_stock(
    request: StockValidationRequest,
    db: Session = Depends(get_db),
):
    """
    Validar se há estoque disponível para os itens solicitados.
    Endpoint público (não requer autenticação).
    
    Args:
        request: Itens para validar
        db: Sessão do banco de dados
        
    Returns:
        StockValidationResponse: Resultado da validação
    """
    unavailable_items = []
    
    # Verificar estoque de cada item
    for item in request.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        if not product:
            unavailable_items.append({
                "product_id": item.product_id,
                "requested_quantity": item.quantity,
                "available_quantity": 0,
                "reason": "Produto não encontrado",
            })
            continue
        
        if product.stock < item.quantity:
            unavailable_items.append({
                "product_id": item.product_id,
                "product_name": product.name,
                "requested_quantity": item.quantity,
                "available_quantity": product.stock,
                "reason": f"Estoque insuficiente. Disponível: {product.stock}",
            })
    
    # Determinar se a validação passou
    is_valid = len(unavailable_items) == 0
    message = "Todos os itens têm estoque disponível" if is_valid else "Alguns itens não têm estoque suficiente"
    
    return StockValidationResponse(
        is_valid=is_valid,
        message=message,
        unavailable_items=unavailable_items,
    )


@router.post("/checkout", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def checkout(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Fazer checkout e criar um pedido.
    Requer autenticação.
    
    Args:
        order_data: Dados do pedido
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        OrderResponse: Dados do pedido criado
        
    Raises:
        HTTPException: Se há erro na validação de estoque ou dados inválidos
    """
    # Validar estoque de todos os itens
    unavailable_items = []
    total_price = 0.0
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {item.product_id} não encontrado",
            )
        
        if product.stock < item.quantity:
            unavailable_items.append({
                "product_id": item.product_id,
                "product_name": product.name,
                "requested_quantity": item.quantity,
                "available_quantity": product.stock,
            })
        
        # Calcular preço total
        total_price += item.price * item.quantity
    
    # Se há itens sem estoque, retornar erro
    if unavailable_items:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "message": "Alguns itens não têm estoque suficiente",
                "unavailable_items": unavailable_items,
            },
        )
    
    # Criar pedido
    new_order = Order(
        user_id=current_user.id,
        total_price=total_price,
        shipping_address=order_data.shipping_address,
        payment_method=order_data.payment_method,
    )
    
    db.add(new_order)
    db.flush()  # Obter o ID do pedido sem fazer commit
    
    # Criar itens do pedido e atualizar estoque
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        # Criar item do pedido
        order_item = OrderItem(
            order_id=new_order.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price=item.price,
        )
        
        # Atualizar estoque do produto
        product.stock -= item.quantity
        
        db.add(order_item)
    
    db.commit()
    db.refresh(new_order)
    
    return new_order


@router.get("/products/{product_id}/available", status_code=status.HTTP_200_OK)
def get_product_availability(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Obter disponibilidade de um produto.
    Endpoint público (não requer autenticação).
    
    Args:
        product_id: ID do produto
        db: Sessão do banco de dados
        
    Returns:
        dict: Informações de disponibilidade
        
    Raises:
        HTTPException: Se o produto não existe
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    return {
        "product_id": product.id,
        "product_name": product.name,
        "available_quantity": product.stock,
        "is_available": product.stock > 0,
        "message": "Produto disponível" if product.stock > 0 else "Produto fora de estoque",
    }