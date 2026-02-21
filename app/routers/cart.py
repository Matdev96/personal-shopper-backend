from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.cart import CartItemCreate, CartItemResponse, CartResponse
from app.models.cart import Cart, CartItem
from app.models.product import Product
from app.models.user import User
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/cart", tags=["Cart"])


@router.get("", response_model=CartResponse)
def get_cart(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Obter o carrinho do usuário.
    Se o carrinho não existe, retorna erro 404.
    
    Args:
        current_user: Usuário autenticado
        db: Sessão do banco de dados
        
    Returns:
        CartResponse: Dados do carrinho
        
    Raises:
        HTTPException: Se o carrinho não existe
    """
    cart = db.query(Cart).filter(Cart.user_id == current_user.id).first()
    
    if not cart:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Carrinho não encontrado. Adicione um item para criar o carrinho.",
        )
    
    return cart


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
    # Verificar se o produto existe
    product = db.query(Product).filter(Product.id == item.product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Produto com ID {item.product_id} não encontrado",
        )
    
    # Verificar se há estoque
    if product.stock < item.quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {product.stock}",
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
        
        if product.stock < new_quantity:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Estoque insuficiente. Disponível: {product.stock}",
            )
        
        cart_item.quantity = new_quantity
    else:
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
    
    # Validar quantidade
    if quantity <= 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quantidade deve ser maior que 0",
        )
    
    # Verificar estoque
    product = db.query(Product).filter(Product.id == cart_item.product_id).first()
    
    if product.stock < quantity:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Estoque insuficiente. Disponível: {product.stock}",
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