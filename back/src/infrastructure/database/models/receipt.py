from sqlalchemy import Column, String, Numeric, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
import uuid
from datetime import datetime
import pytz

from src.infrastructure.database.base import Base


class Receipt(Base):
    __tablename__ = "receipts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    qr_code_data = Column(Text, nullable=True)  # Dados do QR Code da nota fiscal
    access_key = Column(String(44), nullable=True, unique=True, index=True)  # Chave de acesso da NFe (44 caracteres)
    number = Column(String(20), nullable=True)  # Número da nota fiscal
    series = Column(String(10), nullable=True)  # Série da nota fiscal
    issuer_cnpj = Column(String(14), nullable=True)  # CNPJ do emitente
    issuer_name = Column(String(255), nullable=True)  # Nome do emitente
    total_amount = Column(Numeric(15, 2), nullable=True)  # Valor total da nota
    issue_date = Column(DateTime(timezone=True), nullable=True)  # Data de emissão
    items_data = Column(JSON, nullable=True)  # Dados dos itens da nota (JSON)
    raw_data = Column(JSON, nullable=True)  # Dados brutos da nota fiscal (JSON completo)
    notes = Column(Text, nullable=True)
    is_processed = Column(Boolean, default=False, nullable=False)  # Se já foi processada em transação
    
    # Relacionamentos
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False)
    
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), nullable=False)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(pytz.UTC), onupdate=lambda: datetime.now(pytz.UTC), nullable=False)

    # Relacionamentos
    user = relationship("User", back_populates="receipts")
    transactions = relationship("Transaction", back_populates="receipt")

