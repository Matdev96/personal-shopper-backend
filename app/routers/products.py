# app/routers/products.py

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from app.schemas.product import ProductCreate, ProductResponse, ProductUpdate, ProductFilter
from app.models.product import Product
from app.models.category import Category
from app.dependencies import get_db, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/products", tags=["Products"])


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    product_data: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Criar um novo produto.
    Requer autenticação e permissão de admin.
    
    Args:
        product_data: Dados do produto
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Returns:
        ProductResponse: Dados do produto criado
        
    Raises:
        HTTPException: Se a categoria não existe
    """
    # Verificar se a categoria existe
    category = db.query(Category).filter(Category.id == product_data.category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada",
        )
    
    # Criar novo produto
    new_product = Product(
        name=product_data.name,
        description=product_data.description,
        price=product_data.price,
        category_id=product_data.category_id,
        image_url=product_data.image_url,
        stock=product_data.stock,
        is_active=True,
    )
    
    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    
    return new_product


@router.get("", response_model=list[ProductResponse])
def list_products(
    category_id: Optional[int] = Query(None, description="Filtrar por categoria"),
    min_price: Optional[float] = Query(None, ge=0, description="Preço mínimo"),
    max_price: Optional[float] = Query(None, ge=0, description="Preço máximo"),
    search: Optional[str] = Query(None, max_length=255, description="Buscar por nome"),
    is_active: Optional[bool] = Query(None, description="Apenas produtos ativos"),
    skip: int = Query(0, ge=0, description="Paginação - quantos pular"),
    limit: int = Query(10, ge=1, le=100, description="Paginação - quantos retornar"),
    db: Session = Depends(get_db),
):
    """
    Listar produtos com filtros.
    Endpoint público (não requer autenticação).
    
    Args:
        category_id: Filtrar por categoria
        min_price: Preço mínimo
        max_price: Preço máximo
        search: Buscar por nome
        is_active: Apenas produtos ativos
        skip: Quantos produtos pular (paginação)
        limit: Quantos produtos retornar (máximo 100)
        db: Sessão do banco de dados
        
    Returns:
        list[ProductResponse]: Lista de produtos
    """
    query = db.query(Product)
    
    # Filtrar por categoria
    if category_id is not None:
        query = query.filter(Product.category_id == category_id)
    
    # Filtrar por preço mínimo
    if min_price is not None:
        query = query.filter(Product.price >= min_price)
    
    # Filtrar por preço máximo
    if max_price is not None:
        query = query.filter(Product.price <= max_price)
    
    # Buscar por nome
    if search:
        query = query.filter(Product.name.ilike(f"%{search}%"))
    
    # Filtrar por status ativo
    if is_active is not None:
        query = query.filter(Product.is_active == is_active)
    
    # Aplicar paginação
    products = query.offset(skip).limit(limit).all()
    
    return products


@router.get("/{product_id}", response_model=ProductResponse)
def get_product(
    product_id: int,
    db: Session = Depends(get_db),
):
    """
    Obter um produto por ID.
    Endpoint público (não requer autenticação).
    
    Args:
        product_id: ID do produto
        db: Sessão do banco de dados
        
    Returns:
        ProductResponse: Dados do produto
        
    Raises:
        HTTPException: Se o produto não existe
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    return product


@router.put("/{product_id}", response_model=ProductResponse)
def update_product(
    product_id: int,
    product_data: ProductUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar um produto.
    Requer autenticação e permissão de admin.
    
    Args:
        product_id: ID do produto
        product_data: Dados a serem atualizados
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Returns:
        ProductResponse: Dados atualizados do produto
        
    Raises:
        HTTPException: Se o produto não existe ou categoria não existe
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    # Verificar se a nova categoria existe (se foi fornecida)
    if product_data.category_id is not None:
        category = db.query(Category).filter(Category.id == product_data.category_id).first()
        
        if not category:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Categoria não encontrada",
            )
        
        product.category_id = product_data.category_id
    
    # Atualizar campos (se foram fornecidos)
    if product_data.name is not None:
        product.name = product_data.name
    
    if product_data.description is not None:
        product.description = product_data.description
    
    if product_data.price is not None:
        product.price = product_data.price
    
    if product_data.image_url is not None:
        product.image_url = product_data.image_url
    
    if product_data.stock is not None:
        product.stock = product_data.stock
    
    if product_data.is_active is not None:
        product.is_active = product_data.is_active
    
    db.commit()
    db.refresh(product)
    
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Deletar um produto.
    Requer autenticação e permissão de admin.
    
    Args:
        product_id: ID do produto
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se o produto não existe
    """
    product = db.query(Product).filter(Product.id == product_id).first()
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Produto não encontrado",
        )
    
    db.delete(product)
    db.commit()