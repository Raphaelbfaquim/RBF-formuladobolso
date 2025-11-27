"""Add family member permissions

Revision ID: 005_add_family_permissions
Revises: 004_add_system_logs
Create Date: 2025-11-26 13:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '005_add_family_permissions'
down_revision = '642b80338653'  # Aponta para a head atual
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar enum para ModulePermission (se não existir)
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE modulepermission AS ENUM (
                'dashboard', 'transactions', 'accounts', 'categories', 'planning',
                'goals', 'bills', 'transfers', 'calendar', 'investments',
                'receipts', 'reports', 'workspaces', 'ai', 'insights',
                'open_banking', 'education', 'gamification', 'family', 'settings'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Criar tabela family_member_permissions usando o enum existente
    op.execute("""
        CREATE TABLE IF NOT EXISTS family_member_permissions (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            family_member_id UUID NOT NULL REFERENCES family_members(id) ON DELETE CASCADE,
            module modulepermission NOT NULL,
            can_view BOOLEAN NOT NULL DEFAULT true,
            can_edit BOOLEAN NOT NULL DEFAULT false,
            can_delete BOOLEAN NOT NULL DEFAULT false,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """)
    
    op.create_index('ix_family_member_permissions_family_member_id', 'family_member_permissions', ['family_member_id'])
    op.create_index('ix_family_member_permissions_module', 'family_member_permissions', ['module'])


def downgrade() -> None:
    op.drop_index('ix_family_member_permissions_module', table_name='family_member_permissions')
    op.drop_index('ix_family_member_permissions_family_member_id', table_name='family_member_permissions')
    op.drop_table('family_member_permissions')
    op.execute('DROP TYPE modulepermission')

