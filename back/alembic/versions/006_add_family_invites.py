"""Add family invites table

Revision ID: 006_add_family_invites
Revises: 005_add_family_permissions
Create Date: 2025-11-26 14:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '006_add_family_invites'
down_revision = '005_add_family_permissions'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar enum para FamilyInviteStatus
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE familyinvitestatus AS ENUM ('pending', 'accepted', 'expired', 'cancelled');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Criar tabela family_invites
    op.execute("""
        CREATE TABLE IF NOT EXISTS family_invites (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            family_id UUID NOT NULL REFERENCES families(id) ON DELETE CASCADE,
            invited_by UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            email VARCHAR(255) NOT NULL,
            token VARCHAR(255) NOT NULL UNIQUE,
            role familymemberrole NOT NULL,
            status familyinvitestatus NOT NULL DEFAULT 'pending',
            expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
            accepted_at TIMESTAMP WITH TIME ZONE,
            user_id UUID REFERENCES users(id) ON DELETE SET NULL,
            created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
            updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
        );
    """)
    
    op.create_index('ix_family_invites_token', 'family_invites', ['token'])
    op.create_index('ix_family_invites_email', 'family_invites', ['email'])
    op.create_index('ix_family_invites_family_id', 'family_invites', ['family_id'])


def downgrade() -> None:
    op.drop_index('ix_family_invites_family_id', table_name='family_invites')
    op.drop_index('ix_family_invites_email', table_name='family_invites')
    op.drop_index('ix_family_invites_token', table_name='family_invites')
    op.drop_table('family_invites')
    op.execute('DROP TYPE IF EXISTS familyinvitestatus')

