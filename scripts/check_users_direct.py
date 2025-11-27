#!/usr/bin/env python3
"""
Script para verificar usuários diretamente no banco usando SQL síncrono
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'back'))

from sqlalchemy import create_engine, text
from src.shared.config import settings

def check_users():
    """Verifica usuários no banco de dados"""
    print("📊 Verificando usuários no banco de dados...")
    print("")
    
    # Usar URL síncrona
    sync_url = settings.DATABASE_SYNC_URL
    print(f"🔗 Conectando em: {sync_url.split('@')[1] if '@' in sync_url else sync_url}")
    print("")
    
    engine = create_engine(sync_url)
    
    with engine.connect() as conn:
        # Verificar banco conectado
        result = conn.execute(text("SELECT current_database()"))
        db_name = result.scalar()
        print(f"📊 Banco de dados: {db_name}")
        print("")
        
        # Contar usuários
        result = conn.execute(text("SELECT COUNT(*) FROM users"))
        count = result.scalar()
        print(f"👥 Total de usuários: {count}")
        print("")
        
        if count == 0:
            print("⚠️  Nenhum usuário encontrado no banco de dados.")
            print("")
            print("💡 Para criar um usuário:")
            print("   1. Acesse: http://localhost:3000/register")
            print("   2. Ou use a API: POST http://localhost:8000/api/v1/auth/register")
        else:
            # Listar usuários
            result = conn.execute(text("""
                SELECT 
                    id,
                    email,
                    username,
                    full_name,
                    is_active,
                    is_verified,
                    role,
                    created_at
                FROM users
                ORDER BY created_at DESC
                LIMIT 100
            """))
            
            print("=" * 80)
            for idx, row in enumerate(result, 1):
                print(f"👤 Usuário {idx}:")
                print(f"   ID: {row.id}")
                print(f"   Username: {row.username}")
                print(f"   Email: {row.email}")
                print(f"   Nome: {row.full_name or 'N/A'}")
                print(f"   Ativo: {'✅ Sim' if row.is_active else '❌ Não'}")
                print(f"   Verificado: {'✅ Sim' if row.is_verified else '❌ Não'}")
                print(f"   Role: {row.role}")
                print(f"   Criado em: {row.created_at}")
                print("-" * 80)
        
        print("")
        print("✅ Verificação concluída!")

if __name__ == "__main__":
    check_users()

