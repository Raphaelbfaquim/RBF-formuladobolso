"""
Script para inicializar o banco de dados
"""
import asyncio
from sqlalchemy import text
from src.infrastructure.database.base import engine


async def init_db():
    """Cria as tabelas no banco de dados"""
    async with engine.begin() as conn:
        # Verificar se as tabelas já existem
        result = await conn.execute(
            text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_schema = 'public' AND table_name = 'users')")
        )
        exists = result.scalar()
        
        if not exists:
            print("Criando tabelas...")
            from src.infrastructure.database.base import Base
            from src.infrastructure.database.models import *  # noqa
            await conn.run_sync(Base.metadata.create_all)
            print("Tabelas criadas com sucesso!")
        else:
            print("Tabelas já existem.")


if __name__ == "__main__":
    asyncio.run(init_db())

