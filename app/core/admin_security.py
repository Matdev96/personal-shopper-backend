from fastapi import Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.models.user import User
from app.dependencies import get_current_user, get_db


def get_current_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
) -> User:
    """
    Verificar se o usuário autenticado é um admin.
    
    Args:
        current_user: Usuário autenticado
        db: Sessão do banco de dados
    
    Returns:
        User: Usuário admin
    
    Raises:
        HTTPException: Se o usuário não é admin
    """
    # Buscar o usuário no banco para ter dados atualizados
    user = db.query(User).filter(User.id == current_user.id).first()
    
    if not user or not user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso negado. Apenas administradores podem acessar este recurso.",
        )
    
    return user