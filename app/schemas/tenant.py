from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr

# Import moved to avoid circular import


class TenantBase(BaseModel):
    name: str
    kvk: str
    contact_email: EmailStr
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[str] = None
    founded_year: Optional[str] = None
    is_active: bool = True


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    kvk: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    address: Optional[str] = None
    phone: Optional[str] = None
    website: Optional[str] = None
    description: Optional[str] = None
    industry: Optional[str] = None
    employee_count: Optional[str] = None
    founded_year: Optional[str] = None
    is_active: Optional[bool] = None


class TenantRead(TenantBase):
    id: UUID
    created_at: datetime
    user_count: Optional[int] = 0  # Added for UI compatibility
    
    class Config:
        from_attributes = True


class TenantWithAdminCreate(BaseModel):
    """Schema for creating a tenant with an admin user."""
    tenant: TenantCreate
    admin: dict  # Will be validated as UserCreate in the endpoint


class TenantWithAdminResponse(BaseModel):
    """Response schema for tenant with admin creation."""
    tenant: TenantRead
    admin: dict  # User info without password
    temp_password: str
    invitation_sent: bool
