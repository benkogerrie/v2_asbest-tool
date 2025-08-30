"""add_performance_indexes_for_reports

Revision ID: 720883bcbc0d
Revises: 58398eea5e00
Create Date: 2025-08-30 20:19:30.915837

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '720883bcbc0d'
down_revision = '58398eea5e00'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Add performance indexes for reports table
    # Composite index for tenant_id and status (most common filter combination)
    op.create_index('idx_reports_tenant_status', 'reports', ['tenant_id', 'status'])
    
    # Index for uploaded_at (used for sorting)
    op.create_index('idx_reports_uploaded_at', 'reports', ['uploaded_at'])
    
    # Index for filename (used for search and sorting)
    op.create_index('idx_reports_filename', 'reports', ['filename'])
    
    # Index for uploaded_by (for user-specific queries)
    op.create_index('idx_reports_uploaded_by', 'reports', ['uploaded_by'])
    
    # Index for report_audit_logs report_id (for audit queries)
    op.create_index('idx_report_audit_logs_report_id', 'report_audit_logs', ['report_id'])


def downgrade() -> None:
    # Drop indexes in reverse order
    op.drop_index('idx_report_audit_logs_report_id', table_name='report_audit_logs')
    op.drop_index('idx_reports_uploaded_by', table_name='reports')
    op.drop_index('idx_reports_filename', table_name='reports')
    op.drop_index('idx_reports_uploaded_at', table_name='reports')
    op.drop_index('idx_reports_tenant_status', table_name='reports')
