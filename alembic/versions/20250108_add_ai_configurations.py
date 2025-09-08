"""Add AI configurations table

Revision ID: 20250108_add_ai_configurations
Revises: 20250908_add_description
Create Date: 2025-01-08 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20250108_add_ai_configurations'
down_revision = '20250908_add_description'
branch_labels = None
depends_on = None


def upgrade():
    # Create ai_configurations table
    op.create_table('ai_configurations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('provider', sa.String(length=50), nullable=False),
        sa.Column('model', sa.String(length=100), nullable=False),
        sa.Column('api_key', sa.Text(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create index on is_active for faster queries
    op.create_index('ix_ai_configurations_is_active', 'ai_configurations', ['is_active'])


def downgrade():
    # Drop index
    op.drop_index('ix_ai_configurations_is_active', table_name='ai_configurations')
    
    # Drop table
    op.drop_table('ai_configurations')
