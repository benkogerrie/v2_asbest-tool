"""Add description field to prompts table

Revision ID: 20250908_add_description
Revises: 20250907_add_prompts
Create Date: 2025-09-08 10:45:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20250908_add_description'
down_revision = '20250907_add_prompts'
branch_labels = None
depends_on = None


def upgrade():
    # Add description column to prompts table
    op.add_column('prompts', sa.Column('description', sa.Text(), nullable=True))


def downgrade():
    # Remove description column from prompts table
    op.drop_column('prompts', 'description')
