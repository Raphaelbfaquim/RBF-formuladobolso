"""
Testes para endpoints de usuários
"""
import pytest
from fastapi import status


class TestGetCurrentUser:
    """Testes para obter informações do usuário atual"""
    
    def test_get_current_user_success(self, client, test_user_data):
        """Testa obter informações do usuário autenticado"""
        # Criar e fazer login
        client.post("/api/v1/auth/register", json=test_user_data)
        login_response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        token = login_response.json()["access_token"]
        
        # Obter informações do usuário
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
    
    def test_get_current_user_unauthorized(self, client):
        """Testa obter informações sem autenticação"""
        response = client.get("/api/v1/users/me")
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_current_user_invalid_token(self, client):
        """Testa obter informações com token inválido"""
        response = client.get(
            "/api/v1/users/me",
            headers={"Authorization": "Bearer token_invalido"}
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

