"""add_calendar_events

Revision ID: d39fbfdeb1dc
Revises: 8564cb8a52c6
Create Date: 2025-11-25 22:03:26.652715

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'd39fbfdeb1dc'
down_revision = '8564cb8a52c6'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Criar tabela calendar_events
    op.create_table(
        'calendar_events',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_type', sa.Enum('transaction', 'bill', 'goal', 'goal_contribution', 'travel', 'birthday', 'important_event', 'reminder', 'custom', name='calendareventtype'), nullable=False),
        sa.Column('title', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('start_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('all_day', sa.Boolean(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('workspace_id', sa.UUID(), nullable=True),
        sa.Column('family_id', sa.UUID(), nullable=True),
        sa.Column('related_transaction_id', sa.UUID(), nullable=True),
        sa.Column('related_bill_id', sa.UUID(), nullable=True),
        sa.Column('related_goal_id', sa.UUID(), nullable=True),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('location', sa.String(length=255), nullable=True),
        sa.Column('is_shared', sa.Boolean(), nullable=False),
        sa.Column('is_public', sa.Boolean(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_by', sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.ForeignKeyConstraint(['created_by'], ['users.id'], ),
        sa.ForeignKeyConstraint(['workspace_id'], ['workspaces.id'], ),
        sa.ForeignKeyConstraint(['family_id'], ['families.id'], ),
        sa.ForeignKeyConstraint(['related_transaction_id'], ['transactions.id'], ),
        sa.ForeignKeyConstraint(['related_bill_id'], ['bills.id'], ),
        sa.ForeignKeyConstraint(['related_goal_id'], ['goals.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calendar_events_user_id', 'calendar_events', ['user_id'])
    op.create_index('ix_calendar_events_start_date', 'calendar_events', ['start_date'])
    op.create_index('ix_calendar_events_workspace_id', 'calendar_events', ['workspace_id'])
    op.create_index('ix_calendar_events_family_id', 'calendar_events', ['family_id'])
    
    # Criar tabela calendar_event_comments
    op.create_table(
        'calendar_event_comments',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('comment', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['calendar_events.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('ix_calendar_event_comments_event_id', 'calendar_event_comments', ['event_id'])
    op.create_index('ix_calendar_event_comments_user_id', 'calendar_event_comments', ['user_id'])
    
    # Criar tabela calendar_event_participants
    op.create_table(
        'calendar_event_participants',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('event_id', sa.UUID(), nullable=False),
        sa.Column('user_id', sa.UUID(), nullable=False),
        sa.Column('status', sa.Enum('going', 'maybe', 'not_going', 'not_responded', name='eventparticipationstatus'), nullable=False),
        sa.Column('responded_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['event_id'], ['calendar_events.id'], ),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('event_id', 'user_id', name='uq_event_user_participant')
    )
    op.create_index('ix_calendar_event_participants_event_id', 'calendar_event_participants', ['event_id'])
    op.create_index('ix_calendar_event_participants_user_id', 'calendar_event_participants', ['user_id'])


def downgrade() -> None:
    op.drop_index('ix_calendar_event_participants_user_id', table_name='calendar_event_participants')
    op.drop_index('ix_calendar_event_participants_event_id', table_name='calendar_event_participants')
    op.drop_table('calendar_event_participants')
    op.drop_index('ix_calendar_event_comments_user_id', table_name='calendar_event_comments')
    op.drop_index('ix_calendar_event_comments_event_id', table_name='calendar_event_comments')
    op.drop_table('calendar_event_comments')
    op.drop_index('ix_calendar_events_family_id', table_name='calendar_events')
    op.drop_index('ix_calendar_events_workspace_id', table_name='calendar_events')
    op.drop_index('ix_calendar_events_start_date', table_name='calendar_events')
    op.drop_index('ix_calendar_events_user_id', table_name='calendar_events')
    op.drop_table('calendar_events')

