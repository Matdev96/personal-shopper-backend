from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.models.order import Order
from app.schemas.user import UserResponse
from app.core.admin_security import get_current_admin

router = APIRouter(prefix="/admin/users", tags=["Admin - Users"])


@router.get("/", response_model=list[UserResponse])
def list_all_users(
    skip: int = Query(0, ge=0),  # ✅ Parâmetro obrigatório
    limit: int = Query(10, ge=1, le=100),  # ✅ Máximo 100!
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Listar todos os usuários cadastrados.
    Apenas administradores podem acessar.
    
    Args:
        skip: Número de registros a pular (paginação)
        limit: Número máximo de registros a retornar
        current_admin: Admin autenticado
        db: Sessão do banco de dados
    
    Returns:
        list[UserResponse]: Lista de usuários
    """
    users = db.query(User).offset(skip).limit(limit).all()
    return users


@router.get("/{user_id}", response_model=UserResponse)
def get_user_detail(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Obter detalhes de um usuário específico.
    Apenas administradores podem acessar.
    
    Args:
        user_id: ID do usuário
        current_admin: Admin autenticado
        db: Sessão do banco de dados
    
    Returns:
        UserResponse: Dados do usuário
    
    Raises:
        HTTPException: Se usuário não encontrado
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    return user


@router.get("/{user_id}/orders")
def get_user_orders(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Obter todos os pedidos de um usuário específico.
    Apenas administradores podem acessar.
    
    Args:
        user_id: ID do usuário
        current_admin: Admin autenticado
        db: Sessão do banco de dados
    
    Returns:
        list: Lista de pedidos do usuário
    
    Raises:
        HTTPException: Se usuário não encontrado
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    return user.orders


@router.put("/{user_id}/toggle-active", response_model=UserResponse)
def toggle_user_active(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Ativar ou desativar um usuário. Apenas administradores podem acessar."""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    if user.id == current_admin.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Não é possível alterar seu próprio status")
    user.is_active = not user.is_active
    db.commit()
    db.refresh(user)
    return user


@router.get("/orders/all")
def list_all_orders(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """Listar todos os pedidos de todos os usuários. Apenas administradores."""
    orders = db.query(Order).order_by(Order.created_at.desc()).offset(skip).limit(limit).all()
    total = db.query(Order).count()
    return {"items": orders, "total": total}


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(
    user_id: int,
    current_admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    """
    Deletar um usuário.
    Apenas administradores podem acessar.
    
    Args:
        user_id: ID do usuário
        current_admin: Admin autenticado
        db: Sessão do banco de dados
    
    Raises:
        HTTPException: Se usuário não encontrado
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuário não encontrado",
        )
    
    db.delete(user)
    db.commit()
    
    return None