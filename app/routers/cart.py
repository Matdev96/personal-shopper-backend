from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.cart import CartItemCreate, CartItemResponse, CartResponse
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.dependencies import get_db, get_current_user
from typing import List

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obter o carrinho do usuário com todos os itens.
    
    Args:
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        CartResponse: Dados do carrinho com itens
        
    Raises:
        HTTPException: Se o carrinho não existe
    """
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrinho não encontrado",
        )
    
    return cart

@router.get("/items", response_model=List[CartItemResponse])
def list_cart_items(
    skip: int = 0,
    limit: int = 10,
    sort_by: str = "created_at",
    sort_order: str = "desc",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Listar itens do carrinho com paginação e ordenação.
    
    Args:
        skip: Número de registros a pular (padrão: 0)
        limit: Número máximo de registros a retornar (padrão: 10)
        sort_by: Campo para ordenação (created_at, price_at_time)
        sort_order: Ordem de classificação (asc, desc)
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        List[CartItemResponse]: Lista de itens do carrinho
        
    Raises:
        HTTPException: Se o carrinho não existe
    """
    # Validar parâmetros
    if skip < 0:
        skip = 0
    if limit < 1 or limit > 100:
        limit = 10
    if sort_order not in ["asc", "desc"]:
        sort_order = "desc"
    if sort_by not in ["created_at", "price_at_time"]:
        sort_by = "created_at"
    
    # Obter carrinho do usuário
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrinho não encontrado",
        )
    
    # Construir query
    query = db.query(CartItem).filter(CartItem.cart_id == cart.id)
    
    # Aplicar ordenação
    if sort_by == "price_at_time":
        sort_column = CartItem.price_at_time
    else:
        sort_column = CartItem.created_at
    
    if sort_order == "asc":
        query = query.order_by(sort_column.asc())
    else:
        query = query.order_by(sort_column.desc())
    
    # Aplicar paginação
    items = query.offset(skip).limit(limit).all()
    
    return items

@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
def add_item_to_cart(
    item: CartItemCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Adicionar um item ao carrinho.
    Se o carrinho não existe, cria um novo.
    Se o item já existe no carrinho, atualiza a quantidade.
    
    Args:
        item: Dados do item (product_id, quantity)
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        CartItemResponse: Dados do item adicionado
        
    Raises:
        HTTPException: Se o produto não existe ou não há estoque
    """
    # Validar que product_id é válido
    if item.product_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do produto deve ser um número positivo",
        )
    
    # Validar que quantity é válido
    if item.quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade deve ser maior que zero",
        )
    
    if item.quantity > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade não pode exceder 1000 unidades",
        )
    
    # Verificar se o produto existe
    product = db.query(Product).filter(Product.id == item.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {item.product_id} não encontrado",
        )
    
    # Verificar se o produto está ativo
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Produto '{product.name}' não está disponível para compra",
        )
    
    # Verificar se há estoque
    if product.stock < item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente para '{product.name}'. Disponível: {product.stock}, Solicitado: {item.quantity}",
        )
    
    # Obter ou criar carrinho
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        cart = Cart(user_id=current_user.id)
        db.add(cart)
        db.flush()
    
    # Verificar se o item já existe no carrinho
    cart_item = db.query(CartItem).filter(
        CartItem.cart_id == cart.id,
        CartItem.product_id == item.product_id,
    ).first()
    
    if cart_item:
        # Atualizar quantidade
        new_quantity = cart_item.quantity + item.quantity
        
        # Validar nova quantidade
        if new_quantity > 1000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Quantidade total não pode exceder 1000 unidades. Atual: {cart_item.quantity}, Solicitado: {item.quantity}",
            )
        
        # Verificar estoque para nova quantidade
        if product.stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente para '{product.name}'. Disponível: {product.stock}, Total solicitado: {new_quantity}",
            )
        
        cart_item.quantity = new_quantity
    else:
        # Validar limite de itens diferentes no carrinho
        current_items_count = db.query(CartItem).filter(CartItem.cart_id == cart.id).count()
        
        if current_items_count >= 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Carrinho não pode conter mais de 100 produtos diferentes",
            )
        
        # Criar novo item
        cart_item = CartItem(
            cart_id=cart.id,
            product_id=item.product_id,
            quantity=item.quantity,
            price_at_time=product.price,
        )
        db.add(cart_item)
    
    db.commit()
    db.refresh(cart_item)
    
    return cart_item


@router.put("/items/{item_id}", response_model=CartItemResponse)
def update_cart_item(
    item_id: int,
    quantity: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar a quantidade de um item no carrinho.
    
    Args:
        item_id: ID do item do carrinho
        quantity: Nova quantidade (deve ser > 0)
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        CartItemResponse: Dados do item atualizado
        
    Raises:
        HTTPException: Se o item não existe, não pertence ao usuário ou quantidade é inválida
    """
    # Validar item_id
    if item_id <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ID do item deve ser um número positivo",
        )
    
    # Validar quantidade
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade deve ser maior que zero",
        )
    
    if quantity > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade não pode exceder 1000 unidades",
        )
    
    # Verificar se o item existe e pertence ao usuário
    cart_item = db.query(CartItem).join(Cart).filter(
        CartItem.id == item_id,
        Cart.user_id == current_user.id,
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item do carrinho não encontrado",
        )
    
    # Verificar se o produto ainda existe
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Produto associado ao item não existe mais",
        )
    
    # Verificar se o produto ainda está ativo
    if not product.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Produto '{product.name}' não está mais disponível para compra",
        )
    
    # Verificar estoque para nova quantidade
    if product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente para '{product.name}'. Disponível: {product.stock}, Solicitado: {quantity}",
        )
    
    # Atualizar quantidade
    cart_item.quantity = quantity
    db.commit()
    db.refresh(cart_item)
    
    return cart_item


@router.delete("/items/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_item_from_cart(
    item_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Remover um item do carrinho.
    
    Args:
        item_id: ID do item do carrinho
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se o item não existe ou não pertence ao usuário
    """
    # Verificar se o item existe e pertence ao usuário
    cart_item = db.query(CartItem).join(Cart).filter(
        CartItem.id == item_id,
        Cart.user_id == current_user.id,
    ).first()
    
    if not cart_item:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Item do carrinho não encontrado",
        )
    
    db.delete(cart_item)
    db.commit()


@router.delete("", status_code=status.HTTP_204_NO_CONTENT)
def clear_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Limpar todos os itens do carrinho.
    
    Args:
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se o carrinho não existe
    """
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrinho não encontrado",
        )
    
    # Deletar todos os itens do carrinho
    db.query(CartItem).filter(CartItem.cart_id == cart.id).delete()
    db.commit()