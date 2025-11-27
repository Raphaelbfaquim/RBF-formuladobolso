#!/usr/bin/env python3
"""
Script para aplicar migração do Alembic diretamente
"""
import sys
from pathlib import Path

# Adicionar o diretório raiz ao path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

try:
    from alembic.config import Config
    from alembic import command
    from src.shared.config import settings
    
    print("🔧 Configurando Alembic...")
    cfg = Config('alembic.ini')
    
    # Usar a URL de sincronização do settings diretamente no dict
    # Evitar problema de interpolação do ConfigParser com % na senha
    cfg.attributes['connection'] = None
    cfg.set_main_option('sqlalchemy.url', settings.DATABASE_SYNC_URL.replace('%', '%%'))
    
    print("📦 Aplicando migrações...")
    print(f"   Banco: {settings.DATABASE_SYNC_URL.split('@')[-1]}")
    
    command.upgrade(cfg, 'head')
    
    print("✅ Migrações aplicadas com sucesso!")
    print("   Todas as tabelas foram criadas no banco de dados.")
    
except ImportError as e:
    print(f"❌ Erro: {e}")
    print("\n💡 Instale as dependências:")
    print("   pip3 install alembic sqlalchemy psycopg2-binary")
    sys.exit(1)
except Exception as e:
    print(f"❌ Erro ao aplicar migração: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

