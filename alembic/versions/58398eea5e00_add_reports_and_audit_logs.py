"""add_reports_and_audit_logs

Revision ID: 58398eea5e00
Revises: 60129fb6c6f1
Create Date: 2025-08-30 19:20:41.620587

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '58398eea5e00'
down_revision = '60129fb6c6f1'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create reports table
    op.create_table('reports',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('tenant_id', sa.UUID(), nullable=False),
        sa.Column('uploaded_by', sa.UUID(), nullable=False),
        sa.Column('filename', sa.VARCHAR(), nullable=False),
        sa.Column('status', postgresql.ENUM('PROCESSING', 'DONE', 'FAILED', 'DELETED_SOFT', name='reportstatus'), nullable=False),
        sa.Column('score', sa.DOUBLE_PRECISION(precision=53), nullable=True),
        sa.Column('finding_count', sa.INTEGER(), nullable=False),
        sa.Column('uploaded_at', postgresql.TIMESTAMP(), nullable=False),
        sa.Column('source_object_key', sa.VARCHAR(), nullable=False),
        sa.Column('conclusion_object_key', sa.VARCHAR(), nullable=True),
        sa.ForeignKeyConstraint(['tenant_id'], ['tenants.id'], name='reports_tenant_id_fkey'),
        sa.ForeignKeyConstraint(['uploaded_by'], ['users.id'], name='reports_uploaded_by_fkey'),
        sa.PrimaryKeyConstraint('id', name='reports_pkey')
    )
    
    # Create report_audit_logs table
    op.create_table('report_audit_logs',
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('report_id', sa.UUID(), nullable=False),
        sa.Column('actor_user_id', sa.UUID(), nullable=True),
        sa.Column('action', postgresql.ENUM('UPLOAD', 'PROCESS_START', 'PROCESS_DONE', 'PROCESS_FAIL', 'SOFT_DELETE', 'RESTORE', name='auditaction'), nullable=False),
        sa.Column('note', sa.VARCHAR(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), nullable=False),
        sa.ForeignKeyConstraint(['actor_user_id'], ['users.id'], name='report_audit_logs_actor_user_id_fkey'),
        sa.ForeignKeyConstraint(['report_id'], ['reports.id'], name='report_audit_logs_report_id_fkey'),
        sa.PrimaryKeyConstraint('id', name='report_audit_logs_pkey')
    )


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_table('report_audit_logs')
    op.drop_table('reports')
    
    # Drop enums
    op.execute('DROP TYPE IF EXISTS auditaction')
    op.execute('DROP TYPE IF EXISTS reportstatus')
