from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class TransactionFilter(BaseModel):
    """Filtros para busca avançada de transações"""
    search_text: Optional[str] = Field(None, description="Busca por texto (descrição, notas)")
    transaction_type: Optional[str] = Field(None, description="Tipo: income, expense, transfer")
    category_id: Optional[UUID] = Field(None, description="Filtrar por categoria")
    account_id: Optional[UUID] = Field(None, description="Filtrar por conta")
    workspace_id: Optional[UUID] = Field(None, description="Filtrar por workspace")
    min_amount: Optional[Decimal] = Field(None, description="Valor mínimo")
    max_amount: Optional[Decimal] = Field(None, description="Valor máximo")
    start_date: Optional[datetime] = Field(None, description="Data inicial")
    end_date: Optional[datetime] = Field(None, description="Data final")
    status: Optional[str] = Field(None, description="Status: pending, completed, cancelled")
    order_by: Optional[str] = Field("transaction_date", description="Campo para ordenação")
    order_direction: Optional[str] = Field("desc", description="Direção: asc ou desc")
    page: int = Field(1, ge=1, description="Página")
    page_size: int = Field(50, ge=1, le=200, description="Itens por página")


class TransactionSearchResponse(BaseModel):
    """Resposta da busca de transações"""
    transactions: list
    total: int
    page: int
    page_size: int
    total_pages: int

