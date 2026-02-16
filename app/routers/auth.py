# app/routers/auth.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.database import SessionLocal
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from app.dependencies import get_db, get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar um novo usuário.
    
    Args:
        user_data: Dados do usuário (email, username, password, full_name)
        db: Sessão do banco de dados
        
    Returns:
        UserResponse: Dados do usuário criado
        
    Raises:
        HTTPException: Se email ou username já existem
    """
    # Verificar se o email já existe
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado",
        )
    
    # Verificar se o username já existe
    existing_username = db.query(User).filter(User.username == user_data.username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já cadastrado",
        )
    
    # Criar novo usuário
    hashed_password = hash_password(user_data.password)
    
    new_user = User(
        email=user_data.email,
        username=user_data.username,
        password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_admin=False,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    return new_user


@router.post("/login")
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Fazer login e receber um token JWT.
    
    Args:
        credentials: Email e senha do usuário
        db: Sessão do banco de dados
        
    Returns:
        dict: Token de acesso e tipo de token
        
    Raises:
        HTTPException: Se email ou senha estiverem incorretos
    """
    # Buscar usuário pelo email
    user = db.query(User).filter(User.email == credentials.email).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    
    # Verificar a senha
    if not verify_password(credentials.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )
    
    # Verificar se o usuário está ativo
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Usuário inativo",
        )
    
    # Criar token de acesso
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
        },
    }


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Obter informações do usuário autenticado.
    Requer autenticação via JWT.
    
    Args:
        current_user: Usuário autenticado (injetado automaticamente)
        
    Returns:
        UserResponse: Dados do usuário autenticado
    """
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Atualizar dados do usuário autenticado.
    Requer autenticação via JWT.
    
    Args:
        user_update: Dados a serem atualizados
        current_user: Usuário autenticado (injetado automaticamente)
        db: Sessão do banco de dados
        
    Returns:
        UserResponse: Dados atualizados do usuário
        
    Raises:
        HTTPException: Se email ou username já existem
    """
    # Verificar se o novo email já existe (se foi fornecido)
    if user_update.email and user_update.email != current_user.email:
        existing_email = db.query(User).filter(User.email == user_update.email).first()
        if existing_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email já cadastrado",
            )
        current_user.email = user_update.email
    
    # Verificar se o novo username já existe (se foi fornecido)
    if user_update.username and user_update.username != current_user.username:
        existing_username = db.query(User).filter(User.username == user_update.username).first()
        if existing_username:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username já cadastrado",
            )
        current_user.username = user_update.username
    
    # Atualizar full_name (se foi fornecido)
    if user_update.full_name:
        current_user.full_name = user_update.full_name
    
    # Atualizar password (se foi fornecida)
    if user_update.password:
        current_user.password = hash_password(user_update.password)
    
    db.commit()
    db.refresh(current_user)
    
    return current_user