"""Add password reset fields to users

Revision ID: 005_password_reset
Revises: 004_system_logs
Create Date: 2024-01-01 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '005_password_reset'
down_revision = '004_system_logs'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verificar se as colunas já existem
    conn = op.get_bind()
    
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'reset_token'
    """))
    reset_token_exists = result.fetchone() is not None
    
    if not reset_token_exists:
        # Adicionar colunas de reset de senha
        op.add_column('users', sa.Column('reset_token', sa.String(255), nullable=True))
        op.add_column('users', sa.Column('reset_token_expires', sa.DateTime(timezone=True), nullable=True))
        
        # Criar índice para reset_token
        op.create_index('ix_users_reset_token', 'users', ['reset_token'])


def downgrade() -> None:
    # Remover índice
    op.drop_index('ix_users_reset_token', table_name='users')
    
    # Remover colunas
    op.drop_column('users', 'reset_token_expires')
    op.drop_column('users', 'reset_token')

