# app/dependencies.py

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.core.security import decode_token
from app.models.user import User

# Configurar esquema de segurança HTTP Bearer
security = HTTPBearer()

def get_db():
    """
    Dependency para obter a sessão do banco de dados.
    
    Yields:
        Session: Sessão do SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """
    Dependency para obter o usuário autenticado.
    Valida o token JWT e retorna o usuário.
    
    Args:
        credentials: Credenciais HTTP Bearer
        db: Sessão do banco de dados
        
    Returns:
        User: Usuário autenticado
        
    Raises:
        HTTPException: Se o token for inválido ou expirado
    """
    token = credentials.credentials
    
    # Decodificar o token
    payload = decode_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido ou expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extrair o email do payload
    email: str = payload.get("sub")
    
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Buscar o usuário no banco de dados
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário não encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    
    return user


def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """
    Dependency para obter um usuário admin autenticado.
    
    Args:
        current_user: Usuário autenticado
        
    Returns:
        User: Usuário admin autenticado
        
    Raises:
        HTTPException: Se o usuário não for admin
    """
    if not current_user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso restrito a administradores",
        )
    
    return current_user