from pydantic import BaseModel, Field
from typing import Optional, Dict, Any
from uuid import UUID
from datetime import datetime
from decimal import Decimal


class ReceiptBase(BaseModel):
    qr_code_data: Optional[str] = None
    access_key: Optional[str] = Field(None, max_length=44)
    notes: Optional[str] = None


class ReceiptCreate(ReceiptBase):
    pass


class ReceiptUpdate(BaseModel):
    notes: Optional[str] = None
    is_processed: Optional[bool] = None


class ReceiptResponse(BaseModel):
    id: UUID
    qr_code_data: Optional[str] = None
    access_key: Optional[str] = None
    number: Optional[str] = None
    series: Optional[str] = None
    issuer_cnpj: Optional[str] = None
    issuer_name: Optional[str] = None
    total_amount: Optional[Decimal] = None
    issue_date: Optional[datetime] = None
    items_data: Optional[Dict[str, Any]] = None
    raw_data: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    is_processed: bool
    user_id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class QRCodeScanRequest(BaseModel):
    qr_code_data: str = Field(..., min_length=1)


class ProcessReceiptRequest(BaseModel):
    account_id: UUID
    category_id: Optional[UUID] = None
    create_transaction: bool = True

