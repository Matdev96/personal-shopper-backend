# app/models/product.py

from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.sql import func
from app.database import Base

class Product(Base):
    """
    Modelo de Produto.
    Representa a tabela 'products' no banco de dados.
    """
    
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), index=True, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False)
    image_url = Column(String(500), nullable=True)
    stock = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
    
    def __repr__(self):
        return f"<Product(id={self.id}, name={self.name}, price={self.price})>"