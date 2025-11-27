#!/usr/bin/env python3
"""
Script para verificar usuários no banco de dados
"""

import asyncio
import sys
from pathlib import Path

# Adicionar o diretório back ao path (para imports com src.)
project_root = Path(__file__).parent.parent
back_dir = project_root / "back"
sys.path.insert(0, str(back_dir))

# Importar após adicionar ao path
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy import select
from src.infrastructure.database.models.user import User
from src.shared.config import settings


async def check_users():
    """Verifica usuários no banco de dados"""
    try:
        # Criar engine
        engine = create_async_engine(
            settings.DATABASE_URL,
            echo=False,
        )
        
        # Criar sessão
        async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
        
        async with async_session() as session:
            # Buscar todos os usuários
            result = await session.execute(select(User))
            users = result.scalars().all()
            
            print(f"\n📊 USUÁRIOS NO BANCO DE DADOS\n")
            print(f"Total de usuários: {len(users)}\n")
            
            if len(users) == 0:
                print("⚠️  Nenhum usuário encontrado no banco de dados.")
                print("\n💡 Para criar um usuário:")
                print("   1. Acesse: http://localhost:3000/register")
                print("   2. Ou use a API: POST http://localhost:8000/api/v1/auth/register")
            else:
                print("=" * 80)
                for i, user in enumerate(users, 1):
                    print(f"\n👤 Usuário {i}:")
                    print(f"   ID: {user.id}")
                    print(f"   Username: {user.username}")
                    print(f"   Email: {user.email}")
                    print(f"   Ativo: {'✅ Sim' if user.is_active else '❌ Não'}")
                    print(f"   Criado em: {user.created_at}")
                    if user.phone_number:
                        print(f"   Telefone: {user.phone_number}")
                    print("-" * 80)
            
            print(f"\n✅ Verificação concluída!\n")
        
        await engine.dispose()
        
    except Exception as e:
        print(f"\n❌ Erro ao conectar no banco de dados:")
        print(f"   {str(e)}\n")
        print("💡 Verifique:")
        print("   • Se o PostgreSQL está rodando")
        print("   • Se as variáveis de ambiente estão configuradas (.env)")
        print("   • Se o DATABASE_URL está correto")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(check_users())
