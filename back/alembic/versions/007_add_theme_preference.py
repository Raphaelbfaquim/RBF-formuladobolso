"""Add theme_preference to users

Revision ID: 007_theme_preference
Revises: f48e0aa6068b
Create Date: 2024-12-28 00:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = '007_theme_preference'
down_revision = 'f48e0aa6068b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Verificar se a coluna já existe
    conn = op.get_bind()
    
    result = conn.execute(sa.text("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'users' AND column_name = 'theme_preference'
    """))
    theme_preference_exists = result.fetchone() is not None
    
    if not theme_preference_exists:
        # Adicionar coluna theme_preference
        op.add_column('users', sa.Column('theme_preference', sa.String(20), nullable=True, server_default='system'))


def downgrade() -> None:
    # Remover coluna
    op.drop_column('users', 'theme_preference')

