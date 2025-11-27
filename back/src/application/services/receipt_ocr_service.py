from typing import Optional, Dict, Any
import re
import json

try:
    from PIL import Image
    import pytesseract
    import cv2
    import numpy as np
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    Image = None
    pytesseract = None
    cv2 = None
    np = None

from src.infrastructure.database.models.receipt import Receipt


class ReceiptOCRService:
    """Serviço avançado de OCR para notas fiscais"""

    def __init__(self):
        pass

    async def process_image(self, image_path: str) -> Dict[str, Any]:
        """Processa imagem da nota fiscal e extrai dados"""
        if not OCR_AVAILABLE:
            return {"error": "OCR não disponível. Instale: pip install pytesseract opencv-python"}
        
        try:
            # Carregar imagem
            image = cv2.imread(image_path)
            if image is None:
                return {"error": "Não foi possível carregar a imagem"}

            # Pré-processamento
            processed_image = self._preprocess_image(image)

            # OCR
            text = pytesseract.image_to_string(processed_image, lang="por")
            
            # Extrair dados
            data = self._extract_data_from_text(text)
            
            return data
        except Exception as e:
            return {"error": f"Erro no processamento: {str(e)}"}

    def _preprocess_image(self, image):
        """Pré-processa imagem para melhorar OCR"""
        if not OCR_AVAILABLE:
            return image
        # Converter para escala de cinza
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Aplicar threshold
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Reduzir ruído
        denoised = cv2.fastNlMeansDenoising(thresh, None, 10, 7, 21)
        
        return denoised

    def _extract_data_from_text(self, text: str) -> Dict[str, Any]:
        """Extrai dados estruturados do texto OCR"""
        data = {
            "access_key": None,
            "number": None,
            "series": None,
            "issuer_cnpj": None,
            "issuer_name": None,
            "total_amount": None,
            "issue_date": None,
            "items": [],
        }

        # Extrair chave de acesso (44 dígitos)
        access_key_match = re.search(r'\d{44}', text)
        if access_key_match:
            data["access_key"] = access_key_match.group(0)

        # Extrair CNPJ (14 dígitos)
        cnpj_match = re.search(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}|\d{14}', text)
        if cnpj_match:
            data["issuer_cnpj"] = re.sub(r'[^\d]', '', cnpj_match.group(0))

        # Extrair valor total
        amount_patterns = [
            r'Total[:\s]+R\$\s*(\d+[.,]\d{2})',
            r'Valor\s+Total[:\s]+R\$\s*(\d+[.,]\d{2})',
            r'R\$\s*(\d+[.,]\d{2})',
        ]
        for pattern in amount_patterns:
            amount_match = re.search(pattern, text, re.IGNORECASE)
            if amount_match:
                amount_str = amount_match.group(1).replace(',', '.')
                try:
                    data["total_amount"] = float(amount_str)
                except ValueError:
                    pass
                break

        # Extrair data
        date_patterns = [
            r'(\d{2}/\d{2}/\d{4})',
            r'(\d{2}-\d{2}-\d{4})',
            r'(\d{4}-\d{2}-\d{2})',
        ]
        for pattern in date_patterns:
            date_match = re.search(pattern, text)
            if date_match:
                data["issue_date"] = date_match.group(1)
                break

        # Extrair número da nota
        number_match = re.search(r'N[úu]mero[:\s]+(\d+)', text, re.IGNORECASE)
        if number_match:
            data["number"] = number_match.group(1)

        # Extrair série
        series_match = re.search(r'S[ée]rie[:\s]+(\d+)', text, re.IGNORECASE)
        if series_match:
            data["series"] = series_match.group(1)

        return data

    async def process_qr_code_advanced(self, qr_code_data: str) -> Dict[str, Any]:
        """Processa QR Code avançado (formato completo da NFe)"""
        data = {
            "access_key": None,
            "number": None,
            "series": None,
            "issuer_cnpj": None,
            "issuer_name": None,
            "total_amount": None,
            "issue_date": None,
            "items": [],
        }

        # QR Code pode ser URL ou string direta
        if "http" in qr_code_data:
            # É uma URL - extrair parâmetros
            from urllib.parse import urlparse, parse_qs
            parsed = urlparse(qr_code_data)
            params = parse_qs(parsed.query)
            
            if "chNFe" in params:
                data["access_key"] = params["chNFe"][0]
        else:
            # String direta - tentar extrair chave de acesso
            access_key_match = re.search(r'\d{44}', qr_code_data)
            if access_key_match:
                data["access_key"] = access_key_match.group(0)

        # Se tiver chave de acesso, tentar buscar dados da Receita Federal
        if data["access_key"]:
            # TODO: Integrar com API da Receita Federal para buscar dados completos
            pass

        return data

