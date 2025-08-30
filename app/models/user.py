import uuid
from datetime import datetime
from enum import Enum
from typing import Optional

from fastapi_users.db import SQLAlchemyBaseUserTableUUID
from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.database import Base


class UserRole(str, Enum):
    USER = "USER"
    ADMIN = "ADMIN"
    SYSTEM_OWNER = "SYSTEM_OWNER"


class User(SQLAlchemyBaseUserTableUUID, Base):
    __tablename__ = "users"
    
    # FastAPI Users fields (inherited from SQLAlchemyBaseUserTableUUID)
    # id, email, hashed_password, is_active, is_superuser, is_verified
    
    # Custom fields
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relationships
    tenant = relationship("Tenant", back_populates="users")
    
    # Table constraints - Email uniqueness scoped to tenant_id
    __table_args__ = (
        Index('ix_user_email_tenant', 'email', 'tenant_id', unique=True),
    )
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', role='{self.role}')>"
