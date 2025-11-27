#!/usr/bin/env python3
"""
Script para testar registro de usuário via API
"""

import requests
import json
import sys

API_URL = "http://localhost:8000/api/v1"

def test_register():
    """Testa registro de usuário"""
    print("🧪 Testando Registro de Usuário via API\n")
    
    # Dados do usuário de teste
    user_data = {
        "username": "usuario_teste_api",
        "email": "teste_api@formulado.com",
        "password": "senha123456",
        "full_name": "Usuário Teste API"
    }
    
    print(f"📤 Enviando requisição para: {API_URL}/auth/register")
    print(f"📋 Dados: {json.dumps(user_data, indent=2)}\n")
    
    try:
        response = requests.post(
            f"{API_URL}/auth/register",
            json=user_data,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"📥 Status Code: {response.status_code}")
        print(f"📥 Headers: {dict(response.headers)}\n")
        
        if response.status_code == 201:
            user = response.json()
            print("✅ Usuário criado com sucesso!")
            print(f"\n👤 Dados do usuário criado:")
            print(f"   ID: {user.get('id')}")
            print(f"   Username: {user.get('username')}")
            print(f"   Email: {user.get('email')}")
            print(f"   Ativo: {user.get('is_active')}")
            print(f"   Criado em: {user.get('created_at')}")
            return True
        else:
            print(f"❌ Erro ao criar usuário:")
            print(f"   Status: {response.status_code}")
            print(f"   Resposta: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Erro: Não foi possível conectar ao servidor")
        print("   Verifique se o backend está rodando em http://localhost:8000")
        return False
    except requests.exceptions.Timeout:
        print("❌ Erro: Timeout ao conectar ao servidor")
        return False
    except Exception as e:
        print(f"❌ Erro inesperado: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_register()
    sys.exit(0 if success else 1)

