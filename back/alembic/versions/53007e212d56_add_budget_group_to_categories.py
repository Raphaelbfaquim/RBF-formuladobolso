"""add_budget_group_to_categories

Revision ID: 53007e212d56
Revises: c0aaa1242d8c
Create Date: 2025-11-25 20:26:20.307593

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '53007e212d56'
down_revision = 'c0aaa1242d8c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Adicionar campo budget_group na tabela categories
    # Valores possíveis: 'necessities', 'wants', 'savings', ou NULL
    op.add_column('categories', sa.Column('budget_group', sa.String(20), nullable=True))
    
    # Criar índice para melhor performance em consultas
    op.create_index('ix_categories_budget_group', 'categories', ['budget_group'])


def downgrade() -> None:
    # Remover índice
    op.drop_index('ix_categories_budget_group', table_name='categories')
    
    # Remover coluna
    op.drop_column('categories', 'budget_group')

