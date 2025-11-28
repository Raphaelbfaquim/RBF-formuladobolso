#!/usr/bin/env python3
"""
Script para tornar um usuário administrador
Uso: python scripts/make-admin.py <email>
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
from src.infrastructure.database.models.user import User, UserRole
from src.shared.config import settings

async def make_admin(email: str):
    """Torna um usuário administrador"""
    # Criar engine
    engine = create_async_engine(
        settings.DATABASE_URL,
        echo=False
    )
    
    async_session = sessionmaker(
        engine, class_=AsyncSession, expire_on_commit=False
    )
    
    async with async_session() as session:
        # Buscar usuário
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        user = result.scalar_one_or_none()
        
        if not user:
            print(f"❌ Usuário com email '{email}' não encontrado!")
            return False
        
        # Verificar se já é admin
        if user.role == UserRole.ADMIN:
            print(f"✅ Usuário '{email}' já é administrador!")
            return True
        
        # Tornar admin
        user.role = UserRole.ADMIN
        await session.commit()
        await session.refresh(user)
        
        print(f"✅ Usuário '{email}' promovido a administrador com sucesso!")
        print(f"   ID: {user.id}")
        print(f"   Username: {user.username}")
        print(f"   Role: {user.role.value}")
        return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python scripts/make-admin.py <email>")
        print("Exemplo: python scripts/make-admin.py usuario@email.com")
        sys.exit(1)
    
    email = sys.argv[1]
    
    import asyncio
    asyncio.run(make_admin(email))

