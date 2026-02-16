# app/routers/categories.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate
from app.models.category import Category
from app.dependencies import get_db, get_current_admin_user
from app.models.user import User

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(
    category_data: CategoryCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Criar uma nova categoria.
    Requer autenticação e permissão de admin.
    
    Args:
        category_data: Dados da categoria (name, description)
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Returns:
        CategoryResponse: Dados da categoria criada
        
    Raises:
        HTTPException: Se o nome da categoria já existe
    """
    # Verificar se a categoria já existe
    existing_category = db.query(Category).filter(
        Category.name == category_data.name
    ).first()
    
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Categoria com este nome já existe",
        )
    
    # Criar nova categoria
    new_category = Category(
        name=category_data.name,
        description=category_data.description,
    )
    
    db.add(new_category)
    db.commit()
    db.refresh(new_category)
    
    return new_category


@router.get("", response_model=list[CategoryResponse])
def list_categories(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db),
):
    """
    Listar todas as categorias.
    Endpoint público (não requer autenticação).
    
    Args:
        skip: Quantas categorias pular (paginação)
        limit: Quantas categorias retornar (máximo 100)
        db: Sessão do banco de dados
        
    Returns:
        list[CategoryResponse]: Lista de categorias
    """
    # Validar limit
    if limit > 100:
        limit = 100
    
    categories = db.query(Category).offset(skip).limit(limit).all()
    
    return categories


@router.get("/{category_id}", response_model=CategoryResponse)
def get_category(
    category_id: int,
    db: Session = Depends(get_db),
):
    """
    Obter uma categoria por ID.
    Endpoint público (não requer autenticação).
    
    Args:
        category_id: ID da categoria
        db: Sessão do banco de dados
        
    Returns:
        CategoryResponse: Dados da categoria
        
    Raises:
        HTTPException: Se a categoria não existe
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada",
        )
    
    return category


@router.put("/{category_id}", response_model=CategoryResponse)
def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar uma categoria.
    Requer autenticação e permissão de admin.
    
    Args:
        category_id: ID da categoria
        category_data: Dados a serem atualizados
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Returns:
        CategoryResponse: Dados atualizados da categoria
        
    Raises:
        HTTPException: Se a categoria não existe ou nome já existe
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada",
        )
    
    # Verificar se o novo nome já existe (se foi fornecido)
    if category_data.name and category_data.name != category.name:
        existing_category = db.query(Category).filter(
            Category.name == category_data.name
        ).first()
        
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Categoria com este nome já existe",
            )
        
        category.name = category_data.name
    
    # Atualizar descrição (se foi fornecida)
    if category_data.description is not None:
        category.description = category_data.description
    
    db.commit()
    db.refresh(category)
    
    return category


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(
    category_id: int,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """
    Deletar uma categoria.
    Requer autenticação e permissão de admin.
    
    Args:
        category_id: ID da categoria
        current_user: Usuário autenticado (deve ser admin)
        db: Sessão do banco de dados
        
    Raises:
        HTTPException: Se a categoria não existe
    """
    category = db.query(Category).filter(Category.id == category_id).first()
    
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Categoria não encontrada",
        )
    
    db.delete(category)
    db.commit()
