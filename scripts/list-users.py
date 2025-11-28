#!/usr/bin/env python3
"""
Script para listar usuários do sistema
Uso: python scripts/list-users.py
"""
import sys
import os
from pathlib import Path

# Adicionar o diretório raiz ao path
root_dir = Path(__file__).parent.parent
sys.path.insert(0, str(root_dir))

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select
from src.infrastructure.database.models.user import User
from src.shared.config import settings

async def list_users():
    """Lista todos os usuários"""
    # Criar engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Buscar todos os usuários
        stmt = select(User).order_by(User.created_at.desc())
        result = await session.execute(stmt)
        users = result.scalars().all()
        
        if not users:
            print("❌ Nenhum usuário encontrado!")
            return
        
        print(f"\n{'='*80}")
        print(f"Total de usuários: {len(users)}")
        print(f"{'='*80}\n")
        
        print(f"{'Email':<30} {'Username':<20} {'Role':<10} {'Ativo':<8} {'Verificado':<10}")
        print("-" * 80)
        
        for user in users:
            role = user.role.value if hasattr(user.role, 'value') else str(user.role)
            ativo = "✅" if user.is_active else "❌"
            verificado = "✅" if user.is_verified else "❌"
            
            print(f"{user.email:<30} {user.username:<20} {role:<10} {ativo:<8} {verificado:<10}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(list_users())

