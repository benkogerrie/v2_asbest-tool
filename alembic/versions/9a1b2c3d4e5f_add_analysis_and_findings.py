"""Add analysis and findings tables

Revision ID: 9a1b2c3d4e5f
Revises: 830883bcbc0e
Create Date: 2025-09-06 12:30:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9a1b2c3d4e5f'
down_revision = '830883bcbc0e'
branch_labels = None
depends_on = None


def upgrade():
    # Add new columns to reports table
    op.add_column('reports', sa.Column('analysis_version', sa.Text(), nullable=True))
    op.add_column('reports', sa.Column('analysis_duration_ms', sa.Integer(), nullable=True))
    
    # Create analyses table
    op.create_table(
        'analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('report_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('reports.id', ondelete='CASCADE'), index=True, nullable=False),
        sa.Column('engine', sa.Text(), nullable=False),  # "rules"
        sa.Column('engine_version', sa.Text(), nullable=False),  # "rules-1.0.0"
        sa.Column('score', sa.Numeric(5,2), nullable=False),
        sa.Column('summary', sa.Text(), nullable=False),
        sa.Column('rules_passed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('rules_failed', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('duration_ms', sa.Integer(), nullable=False),
        sa.Column('raw_metadata', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    
    # Create findings table
    op.create_table(
        'findings',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('analysis_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('analyses.id', ondelete='CASCADE'), index=True, nullable=False),
        sa.Column('rule_id', sa.Text(), nullable=False),
        sa.Column('section', sa.Text(), nullable=True),
        sa.Column('severity', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='severity_enum'), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
        sa.Column('suggestion', sa.Text(), nullable=True),
        sa.Column('evidence', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('tags', postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
    )


def downgrade():
    # Drop findings table
    op.drop_table('findings')
    
    # Drop analyses table
    op.drop_table('analyses')
    
    # Drop severity enum
    op.execute('DROP TYPE IF EXISTS severity_enum')
    
    # Remove columns from reports table
    op.drop_column('reports', 'analysis_duration_ms')
    op.drop_column('reports', 'analysis_version')
