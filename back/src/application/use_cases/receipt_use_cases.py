from typing import Optional, Dict, Any, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal
from src.domain.repositories.receipt_repository import ReceiptRepository
from src.infrastructure.database.models.receipt import Receipt
from src.shared.exceptions import NotFoundException, ValidationException


class ReceiptUseCases:
    """Casos de uso para gerenciamento de notas fiscais"""

    def __init__(self, receipt_repository: ReceiptRepository):
        self.receipt_repository = receipt_repository

    async def process_qr_code(self, qr_code_data: str, user_id: UUID) -> Receipt:
        """Processa QR Code de nota fiscal"""
        # Extrair dados do QR Code
        # Formato típico: chave de acesso NFe (44 caracteres)
        access_key = self._extract_access_key(qr_code_data)
        
        # Verificar se já existe
        existing = await self.receipt_repository.get_by_access_key(access_key)
        if existing:
            raise ValidationException("Nota fiscal já cadastrada")

        # Criar nota fiscal (dados básicos, pode ser expandido com API da Receita)
        receipt = Receipt(
            qr_code_data=qr_code_data,
            access_key=access_key,
            user_id=user_id,
            is_processed=False,
        )

        return await self.receipt_repository.create(receipt)

    def _extract_access_key(self, qr_code_data: str) -> Optional[str]:
        """Extrai chave de acesso do QR Code"""
        # QR Code de NFe geralmente contém a chave de acesso (44 caracteres)
        # Pode ser uma URL ou string direta
        if len(qr_code_data) >= 44:
            # Tentar encontrar sequência de 44 dígitos
            import re
            match = re.search(r'\d{44}', qr_code_data)
            if match:
                return match.group(0)
        return None

    async def get_receipt(self, receipt_id: UUID) -> Receipt:
        """Obtém uma nota fiscal por ID"""
        receipt = await self.receipt_repository.get_by_id(receipt_id)
        if not receipt:
            raise NotFoundException("Nota fiscal", str(receipt_id))
        return receipt

    async def update_receipt_data(
        self,
        receipt_id: UUID,
        number: Optional[str] = None,
        series: Optional[str] = None,
        issuer_cnpj: Optional[str] = None,
        issuer_name: Optional[str] = None,
        total_amount: Optional[float] = None,
        issue_date: Optional[datetime] = None,
        items_data: Optional[Dict[str, Any]] = None,
        raw_data: Optional[Dict[str, Any]] = None,
    ) -> Receipt:
        """Atualiza dados da nota fiscal"""
        receipt = await self.get_receipt(receipt_id)

        if number:
            receipt.number = number
        if series:
            receipt.series = series
        if issuer_cnpj:
            receipt.issuer_cnpj = issuer_cnpj
        if issuer_name:
            receipt.issuer_name = issuer_name
        if total_amount:
            receipt.total_amount = Decimal(str(total_amount))
        if issue_date:
            receipt.issue_date = issue_date
        if items_data:
            receipt.items_data = items_data
        if raw_data:
            receipt.raw_data = raw_data

        return await self.receipt_repository.update(receipt)

    async def get_user_receipts(self, user_id: UUID) -> List[Receipt]:
        """Obtém todas as notas fiscais de um usuário"""
        return await self.receipt_repository.get_by_user_id(user_id)

