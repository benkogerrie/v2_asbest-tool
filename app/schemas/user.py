from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

from app.models.user import UserRole


class UserBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    role: UserRole = UserRole.USER
    tenant_id: Optional[UUID] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    employee_id: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    email: Optional[EmailStr] = None
    role: Optional[UserRole] = None
    tenant_id: Optional[UUID] = None
    phone: Optional[str] = None
    department: Optional[str] = None
    job_title: Optional[str] = None
    employee_id: Optional[str] = None
    is_active: Optional[bool] = None
    password: Optional[str] = None


class UserRead(UserBase):
    id: UUID
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime
    tenant_name: Optional[str] = None  # Added for UI compatibility
    
    class Config:
        from_attributes = True
