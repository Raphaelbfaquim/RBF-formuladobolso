"""
Testes para endpoints de autenticação
"""
import pytest
from fastapi import status


class TestRegister:
    """Testes para o endpoint de registro"""
    
    def test_register_success(self, client, test_user_data):
        """Testa registro de usuário com sucesso"""
        response = client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )
        
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        
        assert data["email"] == test_user_data["email"]
        assert data["username"] == test_user_data["username"]
        assert data["full_name"] == test_user_data["full_name"]
        assert "id" in data
        assert "created_at" in data
        assert data["is_active"] is True
        assert data["is_verified"] is False
        assert "hashed_password" not in data  # Senha não deve ser retornada
    
    def test_register_duplicate_email(self, client, test_user_data):
        """Testa registro com email duplicado"""
        # Primeiro registro
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Tentativa de registro com mesmo email
        response = client.post(
            "/api/v1/auth/register",
            json=test_user_data
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "email" in response.json()["detail"].lower() or "já está" in response.json()["detail"].lower()
    
    def test_register_duplicate_username(self, client, test_user_data):
        """Testa registro com username duplicado"""
        # Primeiro registro
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Tentativa de registro com mesmo username mas email diferente
        duplicate_data = test_user_data.copy()
        duplicate_data["email"] = "outro@email.com"
        
        response = client.post(
            "/api/v1/auth/register",
            json=duplicate_data
        )
        
        assert response.status_code == status.HTTP_409_CONFLICT
        assert "username" in response.json()["detail"].lower() or "já está" in response.json()["detail"].lower()
    
    def test_register_invalid_email(self, client, test_user_data):
        """Testa registro com email inválido"""
        invalid_data = test_user_data.copy()
        invalid_data["email"] = "email-invalido"
        
        response = client.post(
            "/api/v1/auth/register",
            json=invalid_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_short_password(self, client, test_user_data):
        """Testa registro com senha muito curta"""
        invalid_data = test_user_data.copy()
        invalid_data["password"] = "12345"  # Menos de 8 caracteres
        
        response = client.post(
            "/api/v1/auth/register",
            json=invalid_data
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_register_missing_fields(self, client):
        """Testa registro com campos obrigatórios faltando"""
        response = client.post(
            "/api/v1/auth/register",
            json={"email": "teste@email.com"}  # Faltando username e password
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestLogin:
    """Testes para o endpoint de login"""
    
    def test_login_success(self, client, test_user_data):
        """Testa login com credenciais válidas"""
        # Primeiro criar o usuário
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Tentar fazer login
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": test_user_data["password"]
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        
        assert "access_token" in data
        assert "refresh_token" in data
        assert "token_type" in data
        assert "user" in data
        assert data["user"]["email"] == test_user_data["email"]
    
    def test_login_invalid_email(self, client, test_user_data):
        """Testa login com email inexistente"""
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": "naoexiste@email.com",
                "password": "senha123"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_invalid_password(self, client, test_user_data):
        """Testa login com senha incorreta"""
        # Criar usuário
        client.post("/api/v1/auth/register", json=test_user_data)
        
        # Tentar login com senha errada
        response = client.post(
            "/api/v1/auth/login",
            json={
                "email": test_user_data["email"],
                "password": "senha_errada"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_login_missing_fields(self, client):
        """Testa login com campos faltando"""
        response = client.post(
            "/api/v1/auth/login",
            json={"email": "teste@email.com"}  # Faltando password
        )
        
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

