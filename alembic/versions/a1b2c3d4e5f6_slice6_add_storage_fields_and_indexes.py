"""Slice 6: Add storage fields and indexes to reports

Revision ID: a1b2c3d4e5f6
Revises: 9b2c3d4e5f6a
Create Date: 2025-01-27 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a1b2c3d4e5f6'
down_revision = '9b2c3d4e5f6a'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to reports table for Slice 6
    op.add_column('reports', sa.Column('storage_key', sa.String(), nullable=True))
    op.add_column('reports', sa.Column('checksum', sa.String(), nullable=True))
    op.add_column('reports', sa.Column('file_size', sa.BigInteger(), nullable=True))
    op.add_column('reports', sa.Column('error_message', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('deleted_at', sa.DateTime(), nullable=True))
    
    # Add new audit actions to the enum
    op.execute("ALTER TYPE auditaction ADD VALUE 'REPORT_DOWNLOAD'")
    op.execute("ALTER TYPE auditaction ADD VALUE 'NOTIFICATION_SENT'")
    op.execute("ALTER TYPE auditaction ADD VALUE 'REPORT_PURGE'")
    
    # Create indexes for better performance
    op.create_index('idx_reports_tenant_created', 'reports', ['tenant_id', 'created_at'], unique=False)
    op.create_index('idx_reports_status', 'reports', ['status'], unique=False)
    op.create_index('idx_reports_deleted_at', 'reports', ['deleted_at'], unique=False)


def downgrade():
    # Drop indexes
    op.drop_index('idx_reports_deleted_at', table_name='reports')
    op.drop_index('idx_reports_status', table_name='reports')
    op.drop_index('idx_reports_tenant_created', table_name='reports')
    
    # Remove new columns from reports table
    op.drop_column('reports', 'deleted_at')
    op.drop_column('reports', 'error_message')
    op.drop_column('reports', 'file_size')
    op.drop_column('reports', 'checksum')
    op.drop_column('reports', 'storage_key')
    
    # Note: PostgreSQL doesn't support removing enum values easily
    # The new audit action values will remain but won't be used
