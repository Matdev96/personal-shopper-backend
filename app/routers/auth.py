# app/routers/auth.py

import logging
import secrets
from fastapi import APIRouter, Depends, HTTPException, Request, status, BackgroundTasks
from sqlalchemy.orm import Session
from datetime import timedelta, datetime
from app.database import SessionLocal
from app.schemas.user import UserCreate, UserLogin, UserResponse, UserUpdate
from app.models.user import User
from app.models.password_reset_token import PasswordResetToken
from app.core.security import hash_password, verify_password, create_access_token
from app.core.email import send_reset_email
from app.core.limiter import limiter
from app.dependencies import get_db, get_current_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
@limiter.limit("3/minute")
def register(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Registrar um novo usuário.

    Args:
        user_data: Dados do usuário (email, password, full_name)
        db: Sessão do banco de dados

    Returns:
        UserResponse: Dados do usuário criado

    Raises:
        HTTPException: Se email já existe
    """
    # Verificar se o email já existe
    existing_email = db.query(User).filter(User.email == user_data.email).first()
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email já cadastrado",
        )

    # Derivar username a partir do email (parte antes do @)
    username = user_data.email.split("@")[0]
    
    # Verificar se o username já existe
    existing_username = db.query(User).filter(User.username == username).first()
    if existing_username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username já cadastrado",
        )

    # Criar novo usuário
    hashed_password = hash_password(user_data.password)

    new_user = User(
        email=user_data.email,
        username=username,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_admin=False,
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return new_user


@router.post("/login")
@limiter.limit("5/minute")
def login(request: Request, credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Fazer login e receber um token JWT.
    """
    # Buscar usuário pelo email
    user = db.query(User).filter(User.email == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email ou senha incorretos",
        )

    # Verificar a senha
    if not verify_password(credentials.password, user.hashed_password):
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
    access_token_expires = timedelta(hours=24)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires,
    )

    logger.info("Login realizado com sucesso para: %s", credentials.email)

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "full_name": user.full_name,
            "is_admin": user.is_admin,
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

    # Atualizar full_name (se foi fornecido)
    if user_update.full_name:
        current_user.full_name = user_update.full_name

    # Atualizar password (se foi fornecida)
    if user_update.password:
        current_user.hashed_password = hash_password(user_update.password)

    # Atualizar campos de endereço (se foram fornecidos)
    address_fields = ['cep', 'logradouro', 'numero', 'complemento', 'bairro', 'cidade', 'estado']
    for field in address_fields:
        value = getattr(user_update, field)
        if value is not None:
            setattr(current_user, field, value)

    if user_update.retirar_na_loja is not None:
        current_user.retirar_na_loja = user_update.retirar_na_loja

    db.commit()
    db.refresh(current_user)

    return current_user


@router.post("/forgot-password", status_code=status.HTTP_200_OK)
@limiter.limit("3/minute")
async def forgot_password(
    request: Request,
    background_tasks: BackgroundTasks,
    email: str,
    db: Session = Depends(get_db),
):
    """
    Solicitar recuperação de senha.
    Gera um token seguro, salva no banco e envia email com o link de reset.
    Sempre retorna sucesso para não revelar se o email está cadastrado.
    """
    user = db.query(User).filter(User.email == email).first()

    if user and user.is_active:
        # Invalidar tokens anteriores ainda não usados
        db.query(PasswordResetToken).filter(
            PasswordResetToken.user_id == user.id,
            PasswordResetToken.used == False,
        ).update({"used": True})

        # Gerar token seguro
        token = secrets.token_urlsafe(32)
        expires_at = datetime.utcnow() + timedelta(hours=1)

        reset_token = PasswordResetToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )
        db.add(reset_token)
        db.commit()

        # Enviar email em background para não bloquear a resposta
        background_tasks.add_task(send_reset_email, user.email, token)

    return {"message": "Se este email estiver cadastrado, você receberá as instruções em breve."}


@router.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(
    token: str,
    new_password: str,
    db: Session = Depends(get_db),
):
    """
    Redefinir senha usando o token recebido por email.
    Valida o token (existe, não expirou, não foi usado) e atualiza a senha.
    """
    reset_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.used == False,
    ).first()

    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token inválido ou já utilizado.",
        )

    if datetime.utcnow() > reset_token.expires_at:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token expirado. Solicite um novo link de recuperação.",
        )

    # Validar força da senha (mesmas regras do cadastro)
    if len(new_password) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha deve ter no mínimo 8 caracteres.")
    if not any(c.isupper() for c in new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha deve conter pelo menos uma letra maiúscula.")
    if not any(c.isdigit() for c in new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha deve conter pelo menos um número.")
    if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in new_password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Senha deve conter pelo menos um caractere especial.")

    # Atualizar senha e invalidar token
    user = db.query(User).filter(User.id == reset_token.user_id).first()
    user.hashed_password = hash_password(new_password)
    reset_token.used = True

    db.commit()

    logger.info("Senha redefinida com sucesso para user_id=%s", user.id)
    return {"message": "Senha redefinida com sucesso. Você já pode fazer login."}