from typing import Optional
import httpx
from src.shared.config import settings


class WhatsAppService:
    """Serviço para envio de mensagens WhatsApp"""

    def __init__(
        self,
        api_url: Optional[str] = None,
        api_token: Optional[str] = None,
        phone_number_id: Optional[str] = None,
    ):
        """
        Inicializa o serviço de WhatsApp
        
        Suporta múltiplas APIs:
        - WhatsApp Business API (Meta)
        - Twilio
        - Evolution API
        - Outras APIs compatíveis
        """
        self.api_url = api_url or getattr(settings, "WHATSAPP_API_URL", None)
        self.api_token = api_token or getattr(settings, "WHATSAPP_API_TOKEN", None)
        self.phone_number_id = phone_number_id or getattr(
            settings, "WHATSAPP_PHONE_NUMBER_ID", None
        )

    async def send_message(
        self, phone_number: str, message: str, template: Optional[str] = None
    ) -> bool:
        """
        Envia mensagem WhatsApp
        
        Args:
            phone_number: Número do destinatário (formato: 5511999999999)
            message: Mensagem a ser enviada
            template: Template a ser usado (opcional)
        """
        if not self.api_url or not self.api_token:
            print("WhatsApp não configurado. Verifique as variáveis de ambiente.")
            return False

        try:
            # Formatar número (remover caracteres especiais)
            phone_number = self._format_phone_number(phone_number)

            # Preparar payload baseado no tipo de API
            if "evolution-api" in self.api_url.lower() or "evolution" in self.api_url.lower():
                return await self._send_via_evolution_api(phone_number, message)
            elif "twilio" in self.api_url.lower():
                return await self._send_via_twilio(phone_number, message)
            else:
                # WhatsApp Business API (Meta)
                return await self._send_via_meta_api(phone_number, message, template)

        except Exception as e:
            print(f"Erro ao enviar mensagem WhatsApp: {e}")
            return False

    async def _send_via_meta_api(
        self, phone_number: str, message: str, template: Optional[str] = None
    ) -> bool:
        """Envia via WhatsApp Business API (Meta)"""
        url = f"{self.api_url}/{self.phone_number_id}/messages"
        headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json",
        }
        payload = {
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "text",
            "text": {"body": message},
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            return response.status_code == 200

    async def _send_via_evolution_api(self, phone_number: str, message: str) -> bool:
        """Envia via Evolution API"""
        url = f"{self.api_url}/message/sendText/{self.phone_number_id}"
        headers = {
            "apikey": self.api_token,
            "Content-Type": "application/json",
        }
        payload = {
            "number": phone_number,
            "text": message,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, headers=headers, json=payload)
            return response.status_code == 200

    async def _send_via_twilio(self, phone_number: str, message: str) -> bool:
        """Envia via Twilio"""
        url = f"https://api.twilio.com/2010-04-01/Accounts/{self.api_token}/Messages.json"
        auth = (self.api_token, getattr(settings, "TWILIO_AUTH_TOKEN", ""))
        data = {
            "From": f"whatsapp:{self.phone_number_id}",
            "To": f"whatsapp:{phone_number}",
            "Body": message,
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(url, auth=auth, data=data)
            return response.status_code == 201

    def _format_phone_number(self, phone_number: str) -> str:
        """Formata número de telefone"""
        # Remove caracteres especiais
        cleaned = "".join(filter(str.isdigit, phone_number))
        # Adiciona código do país se não tiver
        if not cleaned.startswith("55") and len(cleaned) == 11:
            cleaned = "55" + cleaned
        return cleaned

    async def send_planning_alert(
        self,
        phone_number: str,
        user_name: str,
        planning_name: str,
        target_amount: float,
        actual_amount: float,
        percentage: float,
        is_over_budget: bool,
    ) -> bool:
        """Envia alerta de planejamento via WhatsApp"""
        if is_over_budget:
            message = self._get_over_budget_message(
                user_name, planning_name, target_amount, actual_amount, percentage
            )
        else:
            message = self._get_on_track_message(
                user_name, planning_name, target_amount, actual_amount, percentage
            )

        return await self.send_message(phone_number, message)

    def _get_over_budget_message(
        self,
        user_name: str,
        planning_name: str,
        target_amount: float,
        actual_amount: float,
        percentage: float,
    ) -> str:
        """Mensagem para quando está fora do planejamento"""
        excess = actual_amount - target_amount
        return f"""⚠️ *Atenção ao Seu Planejamento*

Olá, {user_name}!

Você está *fora do seu planejamento financeiro*!

📊 *{planning_name}*
🎯 Meta: R$ {target_amount:,.2f}
💰 Gasto Real: R$ {actual_amount:,.2f}
📈 Excesso: R$ {excess:,.2f}

Você ultrapassou *{percentage:.1f}%* do seu planejamento.

É importante revisar seus gastos e ajustar seu orçamento para manter suas finanças saudáveis.

💡 *Recomendações:*
• Revise suas despesas recentes
• Identifique gastos desnecessários
• Ajuste seu planejamento se necessário
• Considere reduzir despesas nas próximas semanas

Acesse o FormuladoBolso para mais detalhes.

_FormuladoBolso - Seu gerenciador financeiro pessoal_"""

    def _get_on_track_message(
        self,
        user_name: str,
        planning_name: str,
        target_amount: float,
        actual_amount: float,
        percentage: float,
    ) -> str:
        """Mensagem para quando está no planejamento"""
        remaining = target_amount - actual_amount
        return f"""🎉 *Parabéns!*

Olá, {user_name}!

Você está *no caminho certo*! 🎯

📊 *{planning_name}*
🎯 Meta: R$ {target_amount:,.2f}
💰 Gasto Real: R$ {actual_amount:,.2f}
✅ Restante: R$ {remaining:,.2f}

Você está usando apenas *{percentage:.1f}%* do seu planejamento!

Continue assim! Você está gerenciando muito bem suas finanças. Mantenha o foco e continue seguindo seu planejamento.

💡 *Dicas para continuar no caminho certo:*
• Continue monitorando seus gastos
• Mantenha o controle das despesas
• Celebre suas conquistas financeiras
• Considere investir o que sobrar

Acesse o FormuladoBolso para ver mais detalhes.

_FormuladoBolso - Seu gerenciador financeiro pessoal_"""

