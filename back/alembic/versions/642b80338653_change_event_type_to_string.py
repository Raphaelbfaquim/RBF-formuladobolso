"""change_event_type_to_string

Revision ID: 642b80338653
Revises: d39fbfdeb1dc
Create Date: 2025-11-25 22:34:28.228886

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '642b80338653'
down_revision = 'd39fbfdeb1dc'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Alterar coluna event_type de enum para VARCHAR
    # Primeiro, converter os valores do enum para string
    op.execute("""
        ALTER TABLE calendar_events 
        ALTER COLUMN event_type TYPE VARCHAR(50) 
        USING event_type::text
    """)
    
    # Remover o tipo enum se não estiver sendo usado em outras tabelas
    # (Verificar se há outras colunas usando este enum antes de remover)
    op.execute("DROP TYPE IF EXISTS calendareventtype")


def downgrade() -> None:
    # Recriar o enum apenas se não existir
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE calendareventtype AS ENUM (
                'transaction', 'bill', 'goal', 'goal_contribution', 
                'travel', 'birthday', 'important_event', 'reminder', 'custom'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Alterar coluna de volta para enum
    op.execute("""
        ALTER TABLE calendar_events 
        ALTER COLUMN event_type TYPE calendareventtype 
        USING event_type::calendareventtype
    """)

