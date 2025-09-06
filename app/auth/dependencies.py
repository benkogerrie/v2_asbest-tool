"""
Authentication and authorization dependencies.
"""
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.user import User, UserRole
from app.auth.auth import fastapi_users


async def get_current_user(
    user: User = Depends(fastapi_users.current_user(active=True))
) -> User:
    """Get the current authenticated user."""
    return user


async def get_current_active_user(
    user: User = Depends(fastapi_users.current_user(active=True))
) -> User:
    """Get the current active user."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


async def get_current_system_owner(
    user: User = Depends(get_current_active_user)
) -> User:
    """Get the current user if they are a system owner."""
    if user.role != UserRole.SYSTEM_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System owner access required"
        )
    return user


async def get_current_admin_or_system_owner(
    user: User = Depends(get_current_active_user)
) -> User:
    """Get the current user if they are an admin or system owner."""
    if user.role not in [UserRole.ADMIN, UserRole.SYSTEM_OWNER]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or system owner access required"
        )
    return user


async def get_current_tenant_user(
    user: User = Depends(get_current_active_user),
    session: AsyncSession = Depends(get_db)
) -> User:
    """Get the current user if they belong to a tenant."""
    if user.role == UserRole.SYSTEM_OWNER:
        return user
    
    if not user.tenant_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User must belong to a tenant"
        )
    return user


async def get_current_tenant_admin(
    user: User = Depends(get_current_tenant_user)
) -> User:
    """Get the current user if they are a tenant admin."""
    if user.role == UserRole.SYSTEM_OWNER:
        return user
    
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Tenant admin access required"
        )
    return user
