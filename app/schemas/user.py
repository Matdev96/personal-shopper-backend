from pydantic import BaseModel, Field, EmailStr, validator
from typing import Optional
from datetime import datetime


class UserBase(BaseModel):
    """Base para usuário."""
    email: EmailStr = Field(..., description="Email do usuário (deve ser único)")
    full_name: str = Field(
        ..., 
        min_length=3, 
        max_length=100,
        description="Nome completo do usuário"
    )


class UserCreate(UserBase):
    """Schema para criar um novo usuário."""
    password: str = Field(
        ..., 
        min_length=8, 
        max_length=100,
        description="Senha (mínimo 8 caracteres)"
    )
    
    @validator('password')
    def validate_password(cls, v):
        """Validar força da senha."""
        if not any(char.isupper() for char in v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('Senha deve conter pelo menos um número')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        return v


class UserLogin(BaseModel):
    """Schema para login."""
    email: EmailStr = Field(..., description="Email do usuário")
    password: str = Field(..., description="Senha do usuário")


class UserUpdate(BaseModel):
    """Schema para atualizar usuário."""
    email: Optional[EmailStr] = Field(None, description="Novo email")
    full_name: Optional[str] = Field(
        None,
        min_length=3,
        max_length=100,
        description="Novo nome completo"
    )
    password: Optional[str] = Field(
        None,
        min_length=8,
        max_length=100,
        description="Nova senha"
    )
    # Endereço de entrega
    cep: Optional[str] = Field(None, max_length=9, description="CEP (somente números ou com hífen)")
    logradouro: Optional[str] = Field(None, max_length=200, description="Rua/Avenida")
    numero: Optional[str] = Field(None, max_length=20, description="Número")
    complemento: Optional[str] = Field(None, max_length=100, description="Complemento (opcional)")
    bairro: Optional[str] = Field(None, max_length=100, description="Bairro")
    cidade: Optional[str] = Field(None, max_length=100, description="Cidade")
    estado: Optional[str] = Field(None, max_length=2, description="UF do estado (ex: SP)")
    retirar_na_loja: Optional[bool] = Field(None, description="Preferência de retirada na loja")
    
    @validator('password')
    def validate_password(cls, v):
        """Validar força da senha."""
        if v is None:
            return v
        if not any(char.isupper() for char in v):
            raise ValueError('Senha deve conter pelo menos uma letra maiúscula')
        if not any(char.isdigit() for char in v):
            raise ValueError('Senha deve conter pelo menos um número')
        if not any(char in '!@#$%^&*()_+-=[]{}|;:,.<>?' for char in v):
            raise ValueError('Senha deve conter pelo menos um caractere especial')
        return v


class UserResponse(BaseModel):
    """Schema para resposta de usuário."""
    id: int
    email: str
    full_name: str
    is_admin: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime
    # Endereço de entrega
    cep: Optional[str] = None
    logradouro: Optional[str] = None
    numero: Optional[str] = None
    complemento: Optional[str] = None
    bairro: Optional[str] = None
    cidade: Optional[str] = None
    estado: Optional[str] = None
    retirar_na_loja: bool = False

    class Config:
        from_attributes = True