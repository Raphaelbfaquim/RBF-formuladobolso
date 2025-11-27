"""
Testes para endpoints de contas
"""
import pytest
from fastapi import status


@pytest.fixture
def authenticated_client(client, test_user_data):
    """Cliente autenticado para testes"""
    # Criar usuário e fazer login
    client.post("/api/v1/auth/register", json=test_user_data)
    login_response = client.post(
        "/api/v1/auth/login",
        json={
            "email": test_user_data["email"],
            "password": test_user_data["password"]
        }
    )
    
    token = login_response.json()["access_token"]
    # Criar novo cliente com headers
    from fastapi.testclient import TestClient
    from src.presentation.api.main import app
    authenticated = TestClient(app)
    authenticated.headers.update({"Authorization": f"Bearer {token}"})
    return authenticated


class TestCreateAccount:
    """Testes para criação de contas"""
    
    def test_create_account_success(self, authenticated_client):
        """Testa criação de conta com sucesso"""
        account_data = {
            "name": "Conta Corrente",
            "account_type": "checking",
            "initial_balance": 1000.00,
            "currency": "BRL",
            "description": "Conta corrente principal"
        }
        
        response = authenticated_client.post(
            "/api/v1/accounts/",
            json=account_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["name"] == account_data["name"]
        assert data["account_type"] == account_data["account_type"]
        assert float(data["balance"]) == account_data["initial_balance"]
        assert "id" in data
    
    def test_create_account_unauthorized(self, client):
        """Testa criação de conta sem autenticação"""
        response = client.post(
            "/api/v1/accounts/",
            json={"name": "Conta", "account_type": "checking"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_create_account_missing_fields(self, authenticated_client):
        """Testa criação de conta com campos faltando"""
        response = authenticated_client.post(
            "/api/v1/accounts/",
            json={"name": "Conta"}  # Faltando account_type
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestListAccounts:
    """Testes para listagem de contas"""
    
    def test_list_accounts_success(self, authenticated_client):
        """Testa listagem de contas"""
        # Criar algumas contas
        for i in range(3):
            authenticated_client.post(
                "/api/v1/accounts/",
                json={
                    "name": f"Conta {i+1}",
                    "account_type": "checking",
                    "initial_balance": 100.00 * (i + 1)
                }
            )
        
        # Listar contas
        response = authenticated_client.get("/api/v1/accounts/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
    
    def test_list_accounts_empty(self, authenticated_client):
        """Testa listagem quando não há contas"""
        response = authenticated_client.get("/api/v1/accounts/")
        
        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

