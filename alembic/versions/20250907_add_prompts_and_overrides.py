"""add prompts and prompt_overrides

Revision ID: 20250907_add_prompts
Revises: a1b2c3d4e5f6
Create Date: 2025-09-07
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# --- metadata ---
revision = "20250907_add_prompts"
down_revision = "a1b2c3d4e5f6"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # prompts
    op.create_table(
        "prompts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("role", sa.Text(), nullable=False),  # system|user|tool
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("version", sa.Integer(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),  # draft|active|archived
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.UniqueConstraint("name", "version", name="uq_prompts_name_version"),
    )
    op.create_index("ix_prompts_name_status", "prompts", ["name", "status"], unique=False)

    # prompt_overrides
    op.create_table(
        "prompt_overrides",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, nullable=False),
        sa.Column("prompt_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("prompts.id", ondelete="CASCADE"), nullable=False),
        sa.Column("scope", sa.Text(), nullable=False),  # "global" | "tenant:{id}"
        sa.Column("content_override", sa.Text(), nullable=False),
        sa.Column("status", sa.Text(), nullable=False),  # draft|active
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("NOW()"), nullable=False),
    )
    op.create_index("ix_prompt_overrides_prompt_scope_status", "prompt_overrides", ["prompt_id", "scope", "status"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_prompt_overrides_prompt_scope_status", table_name="prompt_overrides")
    op.drop_table("prompt_overrides")
    op.drop_index("ix_prompts_name_status", table_name="prompts")
    op.drop_table("prompts")
