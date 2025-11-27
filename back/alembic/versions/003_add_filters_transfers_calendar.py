"""Add filters, transfers, scheduled transactions and calendar

Revision ID: 003_filters_transfers
Revises: 002_workspaces
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '003_filters_transfers'
down_revision = '002_workspaces'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verificar se as tabelas já existem
    conn = op.get_bind()
    
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'transfers')"))
    transfers_exists = result.scalar()
    
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'scheduled_transactions')"))
    scheduled_exists = result.scalar()
    
    # Criar tabela transfers apenas se não existir
    if not transfers_exists:
        # Usar tipos ENUM diretamente (assumindo que já existem ou serão criados pelo SQLAlchemy)
        transferstatus_enum = postgresql.ENUM('PENDING', 'COMPLETED', 'CANCELLED', 'FAILED', name='transferstatus', create_type=False)
        
        op.create_table(
            'transfers',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('description', sa.String(length=500), nullable=True),
            sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('status', sa.String(20), nullable=False),  # Usar String temporariamente
            sa.Column('transfer_date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('scheduled_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('from_account_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('to_account_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('from_transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('to_transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['from_account_id'], ['accounts.id'], ),
            sa.ForeignKeyConstraint(['to_account_id'], ['accounts.id'], ),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
            sa.ForeignKeyConstraint(['from_transaction_id'], ['transactions.id'], ),
            sa.ForeignKeyConstraint(['to_transaction_id'], ['transactions.id'], ),
            sa.PrimaryKeyConstraint('id')
        )

    # Criar tabela scheduled_transactions apenas se não existir
    if not scheduled_exists:
        op.create_table(
            'scheduled_transactions',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('description', sa.String(length=500), nullable=False),
            sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
            sa.Column('transaction_type', sa.String(length=20), nullable=False),
            sa.Column('status', sa.String(20), nullable=False),  # Usar String temporariamente
            sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('next_execution_date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('recurrence_type', sa.String(20), nullable=False),  # Usar String temporariamente
            sa.Column('recurrence_day', sa.Integer(), nullable=True),
            sa.Column('recurrence_weekday', sa.Integer(), nullable=True),
            sa.Column('execution_count', sa.Integer(), nullable=False),
            sa.Column('max_executions', sa.Integer(), nullable=True),
            sa.Column('last_execution_date', sa.DateTime(timezone=True), nullable=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('account_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('category_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('workspace_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('auto_execute', sa.Boolean(), nullable=False),
            sa.Column('notes', sa.Text(), nullable=True),
            sa.Column('is_active', sa.Boolean(), nullable=False),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
            sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
            sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Criar tabela transaction_executions
        op.create_table(
            'transaction_executions',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('scheduled_transaction_id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('transaction_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('execution_date', sa.DateTime(timezone=True), nullable=False),
            sa.Column('status', sa.String(length=20), nullable=False),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['scheduled_transaction_id'], ['scheduled_transactions.id'], ),
            sa.ForeignKeyConstraint(['transaction_id'], ['transactions.id'], ),
            sa.PrimaryKeyConstraint('id')
        )


def downgrade() -> None:
    op.drop_table('transaction_executions')
    op.drop_table('scheduled_transactions')
    op.drop_table('transfers')
