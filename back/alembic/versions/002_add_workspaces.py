"""Add workspaces and workspace_id to tables

Revision ID: 002_workspaces
Revises: 001_initial
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_workspaces'
down_revision = '001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela workspaces
    op.create_table(
        'workspaces',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('workspace_type', sa.Enum('PERSONAL', 'FAMILY', 'SHARED', name='workspacetype'), nullable=False),
        sa.Column('owner_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('family_id', postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Criar tabela workspace_members
    op.create_table(
        'workspace_members',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('can_edit', sa.Boolean(), nullable=False),
        sa.Column('can_delete', sa.Boolean(), nullable=False),
        sa.Column('joined_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    # Adicionar workspace_id nas tabelas existentes
    op.add_column('accounts', sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_accounts_workspace', 'accounts', 'workspaces', ['workspace_id'], ['id'])

    op.add_column('transactions', sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_transactions_workspace', 'transactions', 'workspaces', ['workspace_id'], ['id'])

    op.add_column('plannings', sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True))
    op.create_foreign_key('fk_plannings_workspace', 'plannings', 'workspaces', ['workspace_id'], ['id'])


def downgrade() -> None:
    # Remover foreign keys e colunas
    op.drop_constraint('fk_plannings_workspace', 'plannings', type_='foreignkey')
    op.drop_column('plannings', 'workspace_id')

    op.drop_constraint('fk_transactions_workspace', 'transactions', type_='foreignkey')
    op.drop_column('transactions', 'workspace_id')

    op.drop_constraint('fk_accounts_workspace', 'accounts', type_='foreignkey')
    op.drop_column('accounts', 'workspace_id')

    # Remover tabelas
    op.drop_table('workspace_members')
    op.drop_table('workspaces')

