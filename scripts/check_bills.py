#!/usr/bin/env python3
"""
Script para verificar contas a pagar/receber no banco de dados
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'back'))

import asyncio
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy import text
from src.shared.config import settings

async def check_bills():
    """Verifica contas a pagar/receber no banco de dados"""
    print("📊 Verificando contas a pagar/receber no banco de dados...")
    print("")
    
    sync_url = settings.DATABASE_SYNC_URL
    engine = create_async_engine(settings.DATABASE_URL)
    Session = async_sessionmaker(engine)
    
    async with Session() as session:
        # Contar contas
        result = await session.execute(text("SELECT COUNT(*) FROM bills"))
        count = result.scalar()
        print(f"👥 Total de contas: {count}")
        print("")
        
        if count == 0:
            print("⚠️  Nenhuma conta encontrada no banco de dados.")
        else:
            # Listar contas
            result = await session.execute(text("""
                SELECT 
                    id,
                    name,
                    description,
                    bill_type,
                    amount,
                    due_date,
                    status,
                    payment_date,
                    is_recurring,
                    recurrence_type,
                    recurrence_day,
                    user_id,
                    account_id,
                    category_id,
                    created_at,
                    updated_at
                FROM bills
                ORDER BY created_at DESC
                LIMIT 100
            """))
            
            print("=" * 80)
            for idx, row in enumerate(result, 1):
                print(f"📋 Conta {idx}:")
                print(f"   ID: {row.id}")
                print(f"   Nome: {row.name}")
                if row.description:
                    print(f"   Descrição: {row.description}")
                bill_type_text = 'Conta a Pagar' if row.bill_type.lower() == 'expense' else 'Conta a Receber'
                print(f"   Tipo: {row.bill_type} ({bill_type_text})")
                print(f"   Valor: R$ {row.amount}")
                print(f"   Vencimento: {row.due_date}")
                print(f"   Status: {row.status}")
                if row.payment_date:
                    print(f"   Data de Pagamento: {row.payment_date}")
                print(f"   Recorrente: {'✅ Sim' if row.is_recurring else '❌ Não'}")
                if row.is_recurring:
                    print(f"   Tipo de Recorrência: {row.recurrence_type}")
                    if row.recurrence_day:
                        print(f"   Dia do Mês: {row.recurrence_day}")
                print(f"   Usuário ID: {row.user_id}")
                if row.account_id:
                    print(f"   Conta ID: {row.account_id}")
                if row.category_id:
                    print(f"   Categoria ID: {row.category_id}")
                print(f"   Criado em: {row.created_at}")
                print("-" * 80)
        
        print("")
        print("✅ Verificação concluída!")

if __name__ == "__main__":
    asyncio.run(check_bills())

