from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Enum, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class RequestStatus(str, enum.Enum):
    PENDENTE = "pendente"
    EM_BUSCA = "em_busca"
    ENCONTRADO = "encontrado"
    AGUARDANDO_CONFIRMACAO = "aguardando_confirmacao"
    CONFIRMADO = "confirmado"
    AGUARDANDO_SINAL = "aguardando_sinal"
    SINAL_PAGO = "sinal_pago"
    SINAL_CONFIRMADO = "sinal_confirmado"
    COMPRADO = "comprado"
    AGUARDANDO_PAGAMENTO_FINAL = "aguardando_pagamento_final"
    PAGO = "pago"
    ENTREGUE = "entregue"
    NAO_ENCONTRADO = "nao_encontrado"
    CANCELADO = "cancelado"
    ALTERNATIVA_DISPONIVEL = "alternativa_disponivel"


# Transições permitidas por papel
CLIENTE_PODE_CANCELAR = {
    RequestStatus.PENDENTE,
    RequestStatus.EM_BUSCA,
    RequestStatus.ALTERNATIVA_DISPONIVEL,
}
CLIENTE_PODE_CONFIRMAR = {RequestStatus.AGUARDANDO_CONFIRMACAO}

ADMIN_TRANSICOES = {
    RequestStatus.PENDENTE: RequestStatus.EM_BUSCA,
    RequestStatus.EM_BUSCA: RequestStatus.ENCONTRADO,
    RequestStatus.ENCONTRADO: RequestStatus.AGUARDANDO_CONFIRMACAO,
    RequestStatus.SINAL_PAGO: RequestStatus.SINAL_CONFIRMADO,
    RequestStatus.SINAL_CONFIRMADO: RequestStatus.COMPRADO,
    RequestStatus.COMPRADO: RequestStatus.AGUARDANDO_PAGAMENTO_FINAL,
    RequestStatus.PAGO: RequestStatus.ENTREGUE,
}


class ProductRequest(Base):
    """Solicitação de busca de produto feita pelo cliente."""

    __tablename__ = "product_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    # Dados do produto desejado
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=True)
    reference_image_url = Column(String(500), nullable=True)
    preferred_store = Column(String(200), nullable=True)
    size = Column(String(50), nullable=True)
    color = Column(String(50), nullable=True)
    max_budget = Column(Float, nullable=True)
    quantity = Column(Integer, default=1, nullable=False)
    notes = Column(Text, nullable=True)

    # Gerenciado pelo admin
    status = Column(String(50), default=RequestStatus.PENDENTE.value, nullable=False)
    quoted_price = Column(Float, nullable=True)
    found_image_url = Column(String(500), nullable=True)
    admin_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    user = relationship("User", back_populates="product_requests")
    payments = relationship("Payment", back_populates="request", cascade="all, delete-orphan")

    @property
    def deposit_amount(self) -> float:
        """Calcula o valor do sinal (50% do preço cotado)."""
        if self.quoted_price:
            return round(self.quoted_price * 0.5, 2)
        return 0.0

    @property
    def remaining_amount(self) -> float:
        """Calcula o valor restante após o sinal."""
        if self.quoted_price:
            return round(self.quoted_price * 0.5, 2)
        return 0.0

    def __repr__(self):
        return f"<ProductRequest(id={self.id}, title={self.title}, status={self.status})>"
