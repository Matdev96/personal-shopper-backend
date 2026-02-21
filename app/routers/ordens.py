from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.schemas.order import OrderCreate, OrderResponse, OrderItemCreate
from app.models.order import Order, OrderItem, OrderStatus
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.dependencies import get_db, get_current_user
from datetime import datetime
from typing import List

router = APIRouter(prefix="/orders", tags=["Orders"])


@router.get("", response_model=List[OrderResponse])
def list_orders(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 10,
):
    """
    Listar todos os pedidos do usuário.
    
    Args:
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        skip: Número de registros a pular (paginação)
        limit: Número máximo de registros a retornar
        
    Returns:
        List[OrderResponse]: Lista de pedidos do usuário
    """
    orders = db.query(Order).filter(
        Order.user_id == current_user.id
    ).order_by(desc(Order.created_at)).offset(skip).limit(limit).all()
    
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
def get_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obter detalhes de um pedido específico.
    
    Args:
        order_id: ID do pedido
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        OrderResponse: Dados do pedido
        
    Raises:
        HTTPException: Se o pedido não existe ou não pertence ao usuário
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )
    
    return order


@router.post("", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    order_data: OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Criar um novo pedido a partir do carrinho.
    
    Args:
        order_data: Dados do pedido (items, shipping_address, payment_method)
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        OrderResponse: Dados do pedido criado
        
    Raises:
        HTTPException: Se não há itens no carrinho ou estoque insuficiente
    """
    # Validar se há itens no pedido
    if not order_data.items or len(order_data.items) == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Pedido deve conter pelo menos um item",
        )
    
    # Verificar estoque e calcular total
    total_price = 0.0
    order_items_data = []
    
    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        
        if not product:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Produto com ID {item.product_id} não encontrado",
            )
        
        if product.stock < item.quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para {product.name}. Disponível: {product.stock}",
            )
        
        item_total = product.price * item.quantity
        total_price += item_total
        
        order_items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price_at_time": product.price,
        })
    
    # Criar pedido
    order = Order(
        user_id=current_user.id,
        total_price=total_price,
        shipping_address=order_data.shipping_address,
        payment_method=order_data.payment_method,
        status=OrderStatus.PENDING,
    )
    
    db.add(order)
    db.flush()
    
    # Adicionar itens do pedido e atualizar estoque
    for item_data in order_items_data:
        order_item = OrderItem(
            order_id=order.id,
            product_id=item_data["product_id"],
            quantity=item_data["quantity"],
            price_at_time=item_data["price_at_time"],
        )
        db.add(order_item)
        
        # Atualizar estoque do produto
        product = db.query(Product).filter(
            Product.id == item_data["product_id"]
        ).first()
        product.stock -= item_data["quantity"]
    
    # Limpar carrinho do usuário
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    if cart:
        db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    
    db.commit()
    db.refresh(order)
    
    return order


@router.put("/{order_id}/cancel", response_model=OrderResponse)
def cancel_order(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Cancelar um pedido.
    Apenas pedidos com status PENDING podem ser cancelados.
    
    Args:
        order_id: ID do pedido
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        OrderResponse: Dados do pedido cancelado
        
    Raises:
        HTTPException: Se o pedido não existe, não pertence ao usuário ou não pode ser cancelado
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )
    
    if order.status != OrderStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Pedido com status '{order.status.value}' não pode ser cancelado",
        )
    
    # Atualizar status
    order.status = OrderStatus.CANCELLED
    
    # Restaurar estoque
    for item in order.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        product.stock += item.quantity
    
    db.commit()
    db.refresh(order)
    
    return order


@router.get("/{order_id}/status", response_model=dict)
def get_order_status(
    order_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Verificar o status de um pedido.
    
    Args:
        order_id: ID do pedido
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        dict: Status do pedido
        
    Raises:
        HTTPException: Se o pedido não existe ou não pertence ao usuário
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )
    
    return {
        "order_id": order.id,
        "status": order.status.value,
        "created_at": order.created_at,
        "updated_at": order.updated_at,
    }


@router.put("/{order_id}/status", response_model=OrderResponse)
def update_order_status(
    order_id: int,
    new_status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar o status de um pedido.
    Apenas o proprietário do pedido pode atualizar o status.
    
    Args:
        order_id: ID do pedido
        new_status: Novo status (pending, processing, shipped, delivered, cancelled)
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        OrderResponse: Dados do pedido atualizado
        
    Raises:
        HTTPException: Se o pedido não existe, não pertence ao usuário ou status é inválido
    """
    order = db.query(Order).filter(
        Order.id == order_id,
        Order.user_id == current_user.id,
    ).first()
    
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Pedido não encontrado",
        )
    
    # Validar novo status
    valid_statuses = [status.value for status in OrderStatus]
    
    if new_status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Status inválido. Valores válidos: {', '.join(valid_statuses)}",
        )
    
    # Atualizar status
    order.status = OrderStatus(new_status)
    db.commit()
    db.refresh(order)
    
    return order