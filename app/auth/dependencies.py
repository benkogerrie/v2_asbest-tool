from typing import Optional
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.auth import fastapi_users
from app.database import get_db
from app.models.user import User, UserRole
from app.models.tenant import Tenant

# FastAPI Users dependencies
current_active_user = fastapi_users.current_user(active=True)
current_superuser = fastapi_users.current_user(active=True, superuser=True)


async def current_system_owner(
    current_user: User = Depends(current_active_user)
) -> User:
    """Dependency to ensure user is a system owner."""
    if current_user.role != UserRole.SYSTEM_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System owner access required"
        )
    return current_user


async def current_tenant_admin(
    current_user: User = Depends(current_active_user)
) -> User:
    """Dependency to ensure user is a tenant admin."""
    if current_user.role not in [UserRole.ADMIN, UserRole.SYSTEM_OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    return current_user


async def get_user_tenant(
    current_user: User = Depends(current_active_user),
    session: AsyncSession = Depends(get_db)
) -> Optional[Tenant]:
    """Get the tenant for the current user."""
    if current_user.role == UserRole.SYSTEM_OWNER:
        return None
    
    if not current_user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User has no tenant assigned"
        )
    
    result = await session.execute(
        select(Tenant).where(Tenant.id == current_user.tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant
