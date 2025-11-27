from fastapi import APIRouter, Depends, UploadFile, File, status
from typing import Optional, List
from uuid import UUID
from src.presentation.schemas.receipt import (
    ReceiptResponse,
    QRCodeScanRequest,
    ProcessReceiptRequest,
)
from src.presentation.api.dependencies import get_current_active_user
from src.domain.repositories.receipt_repository import ReceiptRepository
from src.infrastructure.repositories.receipt_repository import SQLAlchemyReceiptRepository
from src.application.use_cases.receipt_use_cases import ReceiptUseCases
from src.application.services.receipt_ocr_service import ReceiptOCRService
from src.infrastructure.database.base import get_db
from src.infrastructure.database.models.user import User
from sqlalchemy.ext.asyncio import AsyncSession

router = APIRouter()


def get_receipt_repository(db: AsyncSession = Depends(get_db)) -> ReceiptRepository:
    return SQLAlchemyReceiptRepository(db)


def get_receipt_use_cases(
    receipt_repository: ReceiptRepository = Depends(get_receipt_repository),
) -> ReceiptUseCases:
    return ReceiptUseCases(receipt_repository)


@router.post("/scan-qr-code", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def scan_qr_code(
    qr_data: QRCodeScanRequest,
    use_cases: ReceiptUseCases = Depends(get_receipt_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Escaneia QR Code de uma nota fiscal e cria o cadastro"""
    receipt = await use_cases.process_qr_code(qr_data.qr_code_data, current_user.id)
    return receipt


@router.post("/scan-qr-code-file", response_model=ReceiptResponse, status_code=status.HTTP_201_CREATED)
async def scan_qr_code_file(
    file: UploadFile = File(...),
    use_cases: ReceiptUseCases = Depends(get_receipt_use_cases),
    ocr_service: ReceiptOCRService = Depends(lambda: ReceiptOCRService()),
    current_user: User = Depends(get_current_active_user),
):
    """Escaneia QR Code de uma imagem de nota fiscal"""
    import tempfile
    import os
    
    # Salvar arquivo temporário
    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_file:
        content = await file.read()
        tmp_file.write(content)
        tmp_path = tmp_file.name
    
    try:
        # Processar imagem
        ocr_data = await ocr_service.process_image(tmp_path)
        
        # Criar nota fiscal com dados extraídos
        receipt = await use_cases.process_qr_code(
            qr_code_data=ocr_data.get("access_key", ""),
            user_id=current_user.id,
        )
        
        # Atualizar com dados do OCR
        if ocr_data.get("access_key"):
            receipt = await use_cases.update_receipt_data(
                receipt_id=receipt.id,
                number=ocr_data.get("number"),
                series=ocr_data.get("series"),
                issuer_cnpj=ocr_data.get("issuer_cnpj"),
                total_amount=ocr_data.get("total_amount"),
                issue_date=ocr_data.get("issue_date"),
            )
        
        return receipt
    finally:
        # Remover arquivo temporário
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)


@router.get("/", response_model=List[ReceiptResponse])
async def list_receipts(
    use_cases: ReceiptUseCases = Depends(get_receipt_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Lista todas as notas fiscais do usuário"""
    receipts = await use_cases.get_user_receipts(current_user.id)
    return receipts


@router.get("/{receipt_id}", response_model=ReceiptResponse)
async def get_receipt(
    receipt_id: UUID,
    use_cases: ReceiptUseCases = Depends(get_receipt_use_cases),
    current_user: User = Depends(get_current_active_user),
):
    """Obtém uma nota fiscal específica"""
    receipt = await use_cases.get_receipt(receipt_id)
    return receipt


@router.post("/{receipt_id}/process", status_code=status.HTTP_200_OK)
async def process_receipt_to_transaction(
    receipt_id: UUID,
    process_data: ProcessReceiptRequest,
    current_user: User = Depends(get_current_active_user),
):
    """Processa uma nota fiscal e cria transação(ões)"""
    # TODO: Implementar processamento de nota fiscal para transação
    return {"message": f"Process receipt {receipt_id} to transaction"}
