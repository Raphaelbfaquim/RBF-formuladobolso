"""
Testes para endpoints de transações
"""
import pytest
from fastapi import status
from decimal import Decimal


@pytest.fixture
def account_setup(authenticated_client):
    """Cria uma conta para testes de transações"""
    account_response = authenticated_client.post(
        "/api/v1/accounts/",
        json={
            "name": "Conta Teste",
            "account_type": "checking",
            "initial_balance": 1000.00
        }
    )
    account_id = account_response.json()["id"]
    return account_id


class TestCreateTransaction:
    """Testes para criação de transações"""
    
    def test_create_expense_success(self, authenticated_client, account_setup):
        """Testa criação de despesa"""
        transaction_data = {
            "description": "Compra no supermercado",
            "amount": 150.50,
            "transaction_type": "expense",
            "transaction_date": "2024-01-15T10:00:00Z",
            "account_id": account_setup
        }
        
        response = authenticated_client.post(
            "/api/v1/transactions/",
            json=transaction_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["description"] == transaction_data["description"]
        assert float(data["amount"]) == transaction_data["amount"]
        assert data["transaction_type"] == transaction_data["transaction_type"]
        assert data["account_id"] == account_setup
        
        # Verificar se o saldo da conta foi atualizado
        account_response = authenticated_client.get(f"/api/v1/accounts/{account_setup}")
        account = account_response.json()
        assert float(account["balance"]) == 849.50  # 1000 - 150.50
    
    def test_create_income_success(self, authenticated_client, account_setup):
        """Testa criação de receita"""
        transaction_data = {
            "description": "Salário",
            "amount": 5000.00,
            "transaction_type": "income",
            "transaction_date": "2024-01-15T10:00:00Z",
            "account_id": account_setup
        }
        
        response = authenticated_client.post(
            "/api/v1/transactions/",
            json=transaction_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        
        # Verificar se o saldo foi atualizado
        account_response = authenticated_client.get(f"/api/v1/accounts/{account_setup}")
        account = account_response.json()
        assert float(account["balance"]) == 6000.00  # 1000 + 5000
    
    def test_create_transaction_unauthorized(self, client, account_setup):
        """Testa criação de transação sem autenticação"""
        response = client.post(
            "/api/v1/transactions/",
            json={
                "description": "Teste",
                "amount": 100.00,
                "transaction_type": "expense",
                "account_id": account_setup
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestListTransactions:
    """Testes para listagem de transações"""
    
    def test_list_transactions_success(self, authenticated_client, account_setup):
        """Testa listagem de transações"""
        # Criar algumas transações
        for i in range(3):
            authenticated_client.post(
                "/api/v1/transactions/",
                json={
                    "description": f"Transação {i+1}",
                    "amount": 50.00 * (i + 1),
                    "transaction_type": "expense",
                    "transaction_date": "2024-01-15T10:00:00Z",
                    "account_id": account_setup
                }
            )
        
        # Listar transações
        response = authenticated_client.get("/api/v1/transactions/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

