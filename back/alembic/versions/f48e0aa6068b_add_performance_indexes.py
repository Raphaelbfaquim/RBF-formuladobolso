"""add_performance_indexes

Revision ID: f48e0aa6068b
Revises: f48e0aa6068b
Create Date: 2025-11-27 03:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'f48e0aa6068b'
down_revision = '006_add_family_invites'  # Ajustar conforme necessário
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Índices para tabela transactions (críticos para performance com 1000+ contas)
    op.create_index(
        'ix_transactions_account_id',
        'transactions',
        ['account_id'],
        unique=False
    )
    op.create_index(
        'ix_transactions_user_id',
        'transactions',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_transactions_transaction_date',
        'transactions',
        ['transaction_date'],
        unique=False
    )
    op.create_index(
        'ix_transactions_account_date',
        'transactions',
        ['account_id', 'transaction_date'],
        unique=False
    )
    op.create_index(
        'ix_transactions_user_date',
        'transactions',
        ['user_id', 'transaction_date'],
        unique=False
    )
    
    # Índices para tabela accounts (críticos para queries de família)
    op.create_index(
        'ix_accounts_owner_id',
        'accounts',
        ['owner_id'],
        unique=False
    )
    op.create_index(
        'ix_accounts_family_id',
        'accounts',
        ['family_id'],
        unique=False
    )
    op.create_index(
        'ix_accounts_owner_active',
        'accounts',
        ['owner_id', 'is_active'],
        unique=False
    )
    
    # Índices para tabela family_members (já existe composto, mas adicionar individuais)
    op.create_index(
        'ix_family_members_user_id',
        'family_members',
        ['user_id'],
        unique=False
    )
    op.create_index(
        'ix_family_members_family_id',
        'family_members',
        ['family_id'],
        unique=False
    )


def downgrade() -> None:
    op.drop_index('ix_family_members_family_id', table_name='family_members')
    op.drop_index('ix_family_members_user_id', table_name='family_members')
    op.drop_index('ix_accounts_owner_active', table_name='accounts')
    op.drop_index('ix_accounts_family_id', table_name='accounts')
    op.drop_index('ix_accounts_owner_id', table_name='accounts')
    op.drop_index('ix_transactions_user_date', table_name='transactions')
    op.drop_index('ix_transactions_account_date', table_name='transactions')
    op.drop_index('ix_transactions_transaction_date', table_name='transactions')
    op.drop_index('ix_transactions_user_id', table_name='transactions')
    op.drop_index('ix_transactions_account_id', table_name='transactions')
