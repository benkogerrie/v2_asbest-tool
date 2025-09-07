# app/models/prompt.py
from __future__ import annotations
import uuid
from enum import Enum
from datetime import datetime
from typing import List, Optional

from sqlalchemy.orm import relationship, Mapped, mapped_column, declarative_mixin
from sqlalchemy import (
    Text,
    Integer,
    ForeignKey,
    Index,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from app.database import Base  # zorg dat dit jullie declarative Base is (SQLAlchemy 2.x)

# ---- Enums (als Python Enum; DB-kant laten we Text + app-validatie) ----

class PromptRole(str, Enum):
    system = "system"
    user = "user"
    tool = "tool"

class PromptStatus(str, Enum):
    draft = "draft"
    active = "active"
    archived = "archived"

class OverrideStatus(str, Enum):
    draft = "draft"
    active = "active"

# ---- Timestamps mixin ----

@declarative_mixin
class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(
        default=None,
        server_default=text("NOW()"),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        default=None,
        server_default=text("NOW()"),
        nullable=False,
    )

# ---- Models ----

class Prompt(Base, TimestampMixin):
    __tablename__ = "prompts"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    role: Mapped[str] = mapped_column(Text, nullable=False)  # gebruik PromptRole in applicatielaag
    content: Mapped[str] = mapped_column(Text, nullable=False)
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)  # gebruik PromptStatus in applicatielaag

    overrides: Mapped[List["PromptOverride"]] = relationship(
        "PromptOverride",
        back_populates="prompt",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    __table_args__ = (
        UniqueConstraint("name", "version", name="uq_prompts_name_version"),
        Index("ix_prompts_name_status", "name", "status"),
    )

    # Helpers (optioneel; handig voor services)
    def is_active(self) -> bool:
        return self.status == PromptStatus.active.value

    def is_archived(self) -> bool:
        return self.status == PromptStatus.archived.value


class PromptOverride(Base, TimestampMixin):
    __tablename__ = "prompt_overrides"

    id: Mapped[uuid.UUID] = mapped_column(PG_UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    prompt_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("prompts.id", ondelete="CASCADE"),
        nullable=False,
    )
    scope: Mapped[str] = mapped_column(Text, nullable=False)  # "global" | "tenant:{id}"
    content_override: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[str] = mapped_column(Text, nullable=False)  # gebruik OverrideStatus in applicatielaag

    prompt: Mapped[Prompt] = relationship("Prompt", back_populates="overrides", lazy="joined")

    __table_args__ = (
        Index("ix_prompt_overrides_prompt_scope_status", "prompt_id", "scope", "status"),
    )

    # Helpers (optioneel)
    def is_active(self) -> bool:
        return self.status == OverrideStatus.active.value
