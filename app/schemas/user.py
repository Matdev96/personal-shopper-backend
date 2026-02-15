# app/schemas/user.py

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class UserCreate(BaseModel):
    """
    Schema para criar um novo usuário.
    Usado no endpoint de registro.
    """
    email: EmailStr = Field(..., description="Email único do usuário")
    username: str = Field(..., min_length=3, max_length=100, description="Nome de usuário único")
    password: str = Field(..., min_length=6, description="Senha com no mínimo 6 caracteres")
    full_name: Optional[str] = Field(None, max_length=255, description="Nome completo do usuário")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "matheus@example.com",
                "username": "matheus_dias",
                "password": "senha123",
                "full_name": "Matheus Dias"
            }
        }


class UserLogin(BaseModel):
    """
    Schema para fazer login.
    Usado no endpoint de autenticação.
    """
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")

    class Config:
        json_schema_extra = {
            "example": {
                "email": "matheus@example.com",
                "password": "senha123"
            }
        }


class UserResponse(BaseModel):
    """
    Schema para retornar dados do usuário.
    Nunca retorna a senha!
    """
    id: int
    email: str
    username: str
    full_name: Optional[str]
    is_active: bool
    is_admin: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "email": "matheus@example.com",
                "username": "matheus_dias",
                "full_name": "Matheus Dias",
                "is_active": True,
                "is_admin": False,
                "created_at": "2026-02-15T10:30:00",
                "updated_at": "2026-02-15T10:30:00"
            }
        }


class UserUpdate(BaseModel):
    """
    Schema para atualizar dados do usuário.
    Todos os campos são opcionais.
    """
    email: Optional[EmailStr] = None
    username: Optional[str] = Field(None, min_length=3, max_length=100)
    full_name: Optional[str] = Field(None, max_length=255)
    password: Optional[str] = Field(None, min_length=6)

    class Config:
        json_schema_extra = {
            "example": {
                "email": "novo_email@example.com",
                "full_name": "Novo Nome"
            }
        }