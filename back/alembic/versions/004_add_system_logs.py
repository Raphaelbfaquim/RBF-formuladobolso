"""Add system logs table

Revision ID: 004_system_logs
Revises: 003_filters_transfers
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '004_system_logs'
down_revision = '003_filters_transfers'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verificar se a tabela já existe
    conn = op.get_bind()
    result = conn.execute(sa.text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'system_logs')"))
    logs_exists = result.scalar()
    
    if not logs_exists:
        # Criar enums
        op.execute("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'loglevel') THEN
                    CREATE TYPE loglevel AS ENUM ('debug', 'info', 'warning', 'error', 'critical');
                END IF;
            END $$;
        """)
        
        op.execute("""
            DO $$ BEGIN
                IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'logcategory') THEN
                    CREATE TYPE logcategory AS ENUM (
                        'auth', 'transaction', 'account', 'planning', 'user', 'system',
                        'api', 'database', 'notification', 'integration', 'security',
                        'performance', 'workspace', 'transfer', 'scheduled', 'calendar'
                    );
                END IF;
            END $$;
        """)
        
        # Criar tabela system_logs
        op.create_table(
            'system_logs',
            sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
            sa.Column('level', sa.String(20), nullable=False),  # Usar String temporariamente
            sa.Column('category', sa.String(20), nullable=False),  # Usar String temporariamente
            sa.Column('message', sa.Text(), nullable=False),
            sa.Column('details', postgresql.JSON(), nullable=True),
            sa.Column('user_id', postgresql.UUID(as_uuid=True), nullable=True),
            sa.Column('ip_address', sa.String(length=45), nullable=True),
            sa.Column('user_agent', sa.String(length=500), nullable=True),
            sa.Column('request_id', sa.String(length=100), nullable=True),
            sa.Column('error_type', sa.String(length=200), nullable=True),
            sa.Column('error_message', sa.Text(), nullable=True),
            sa.Column('stack_trace', sa.Text(), nullable=True),
            sa.Column('exception_data', postgresql.JSON(), nullable=True),
            sa.Column('execution_time_ms', sa.String(length=20), nullable=True),
            sa.Column('memory_usage_mb', sa.String(length=20), nullable=True),
            sa.Column('endpoint', sa.String(length=500), nullable=True),
            sa.Column('method', sa.String(length=10), nullable=True),
            sa.Column('status_code', sa.String(length=10), nullable=True),
            sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
            sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
            sa.PrimaryKeyConstraint('id')
        )
        
        # Criar índices
        op.create_index('ix_system_logs_level', 'system_logs', ['level'])
        op.create_index('ix_system_logs_category', 'system_logs', ['category'])
        op.create_index('ix_system_logs_user_id', 'system_logs', ['user_id'])
        op.create_index('ix_system_logs_request_id', 'system_logs', ['request_id'])
        op.create_index('ix_system_logs_created_at', 'system_logs', ['created_at'])
        op.create_index('idx_log_level_category', 'system_logs', ['level', 'category'])
        op.create_index('idx_log_user_created', 'system_logs', ['user_id', 'created_at'])
        op.create_index('idx_log_error_levels', 'system_logs', ['level', 'created_at'])


def downgrade() -> None:
    op.drop_index('idx_log_error_levels', table_name='system_logs')
    op.drop_index('idx_log_user_created', table_name='system_logs')
    op.drop_index('idx_log_level_category', table_name='system_logs')
    op.drop_index('ix_system_logs_created_at', table_name='system_logs')
    op.drop_index('ix_system_logs_request_id', table_name='system_logs')
    op.drop_index('ix_system_logs_user_id', table_name='system_logs')
    op.drop_index('ix_system_logs_category', table_name='system_logs')
    op.drop_index('ix_system_logs_level', table_name='system_logs')
    op.drop_table('system_logs')

