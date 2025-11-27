"""add_savings_category_to_goals

Revision ID: 8564cb8a52c6
Revises: 53007e212d56
Create Date: 2025-11-25 21:47:45.998123

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '8564cb8a52c6'
down_revision = '53007e212d56'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column('goals', sa.Column('savings_category_id', sa.UUID(), nullable=True))
    op.add_column('goals', sa.Column('auto_contribution_percentage', sa.Numeric(5, 2), nullable=True))
    op.create_foreign_key('fk_goals_savings_category', 'goals', 'categories', ['savings_category_id'], ['id'])
    op.create_index('ix_goals_savings_category_id', 'goals', ['savings_category_id'])


def downgrade() -> None:
    op.drop_index('ix_goals_savings_category_id', table_name='goals')
    op.drop_constraint('fk_goals_savings_category', 'goals', type_='foreignkey')
    op.drop_column('goals', 'auto_contribution_percentage')
    op.drop_column('goals', 'savings_category_id')

