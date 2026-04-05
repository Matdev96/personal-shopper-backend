from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base
import enum


class PaymentType(str, enum.Enum):
    SINAL = "sinal"
    FINAL = "final"


class PaymentStatus(str, enum.Enum):
    PENDENTE = "pendente"
    CONFIRMADO = "confirmado"
    REJEITADO = "rejeitado"


class Payment(Base):
    """Registro de pagamento vinculado a uma solicitação de produto."""

    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("product_requests.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)

    type = Column(String(20), nullable=False)          # sinal | final
    amount = Column(Float, nullable=False)
    payment_method = Column(String(50), nullable=False) # pix | transferencia | dinheiro | cartao
    payment_date = Column(DateTime, nullable=False)
    receipt_url = Column(String(500), nullable=True)
    status = Column(String(20), default=PaymentStatus.PENDENTE.value, nullable=False)
    admin_notes = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relacionamentos
    request = relationship("ProductRequest", back_populates="payments")
    user = relationship("User", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, type={self.type}, amount={self.amount}, status={self.status})>"
