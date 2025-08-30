from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, EmailStr


class TenantBase(BaseModel):
    name: str
    kvk: str
    contact_email: EmailStr
    is_active: bool = True


class TenantCreate(TenantBase):
    pass


class TenantUpdate(BaseModel):
    name: Optional[str] = None
    kvk: Optional[str] = None
    contact_email: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class TenantRead(TenantBase):
    id: UUID
    created_at: datetime
    
    class Config:
        from_attributes = True
