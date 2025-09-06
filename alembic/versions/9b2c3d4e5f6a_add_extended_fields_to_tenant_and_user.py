"""Add extended fields to tenant and user models

Revision ID: 9b2c3d4e5f6a
Revises: 9a1b2c3d4e5f
Create Date: 2025-09-06 20:35:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '9b2c3d4e5f6a'
down_revision = '9a1b2c3d4e5f'
branch_labels = None
depends_on = None


def upgrade():
    # Add extended fields to tenants table
    op.add_column('tenants', sa.Column('address', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('website', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('description', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('industry', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('employee_count', sa.String(), nullable=True))
    op.add_column('tenants', sa.Column('founded_year', sa.String(), nullable=True))
    
    # Add extended fields to users table
    op.add_column('users', sa.Column('phone', sa.String(), nullable=True))
    op.add_column('users', sa.Column('department', sa.String(), nullable=True))
    op.add_column('users', sa.Column('job_title', sa.String(), nullable=True))
    op.add_column('users', sa.Column('employee_id', sa.String(), nullable=True))


def downgrade():
    # Remove extended fields from users table
    op.drop_column('users', 'employee_id')
    op.drop_column('users', 'job_title')
    op.drop_column('users', 'department')
    op.drop_column('users', 'phone')
    
    # Remove extended fields from tenants table
    op.drop_column('tenants', 'founded_year')
    op.drop_column('tenants', 'employee_count')
    op.drop_column('tenants', 'industry')
    op.drop_column('tenants', 'description')
    op.drop_column('tenants', 'website')
    op.drop_column('tenants', 'phone')
    op.drop_column('tenants', 'address')
