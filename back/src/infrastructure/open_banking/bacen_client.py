from typing import Optional, Dict, List
import httpx
from src.shared.config import settings


class BacenOpenBankingClient:
    """Cliente para integração com Open Banking do Banco Central"""

    def __init__(
        self,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        base_url: str = "https://api.bacen.gov.br/open-banking",
    ):
        self.client_id = client_id or getattr(settings, "OPEN_BANKING_CLIENT_ID", None)
        self.client_secret = client_secret or getattr(settings, "OPEN_BANKING_CLIENT_SECRET", None)
        self.base_url = base_url
        self.access_token: Optional[str] = None

    async def authenticate(self) -> bool:
        """Autentica e obtém access token"""
        if not self.client_id or not self.client_secret:
            return False

        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/oauth/token",
                    data={
                        "grant_type": "client_credentials",
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                    },
                )
                if response.status_code == 200:
                    data = response.json()
                    self.access_token = data.get("access_token")
                    return True
        except Exception as e:
            print(f"Erro na autenticação Open Banking: {e}")

        return False

    async def get_accounts(self, user_consent_token: str) -> List[Dict]:
        """Obtém contas do usuário"""
        if not await self._ensure_authenticated():
            return []

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "x-user-consent": user_consent_token,
                }
                response = await client.get(f"{self.base_url}/accounts", headers=headers)
                if response.status_code == 200:
                    return response.json().get("data", [])
        except Exception as e:
            print(f"Erro ao obter contas: {e}")

        return []

    async def get_transactions(
        self, user_consent_token: str, account_id: str, start_date: str, end_date: str
    ) -> List[Dict]:
        """Obtém transações de uma conta"""
        if not await self._ensure_authenticated():
            return []

        try:
            async with httpx.AsyncClient() as client:
                headers = {
                    "Authorization": f"Bearer {self.access_token}",
                    "x-user-consent": user_consent_token,
                }
                params = {
                    "account_id": account_id,
                    "start_date": start_date,
                    "end_date": end_date,
                }
                response = await client.get(
                    f"{self.base_url}/transactions", headers=headers, params=params
                )
                if response.status_code == 200:
                    return response.json().get("data", [])
        except Exception as e:
            print(f"Erro ao obter transações: {e}")

        return []

    async def _ensure_authenticated(self) -> bool:
        """Garante que está autenticado"""
        if not self.access_token:
            return await self.authenticate()
        return True


class OpenBankingService:
    """Serviço de Open Banking"""

    def __init__(self):
        self.bacen_client = BacenOpenBankingClient()

    async def sync_user_accounts(self, user_id: str, consent_token: str) -> List[Dict]:
        """Sincroniza contas do usuário via Open Banking"""
        accounts = await self.bacen_client.get_accounts(consent_token)
        return accounts

    async def sync_account_transactions(
        self, user_id: str, consent_token: str, account_id: str, days: int = 30
    ) -> List[Dict]:
        """Sincroniza transações de uma conta"""
        from datetime import datetime, timedelta
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        transactions = await self.bacen_client.get_transactions(
            consent_token,
            account_id,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
        )
        return transactions

