"""
Authentication and authorization dependencies.
"""
from fastapi import Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uuid
import base64
import json

from app.database import get_db
from app.models.user import User, UserRole


async def get_current_user(
    request: Request,
    session: AsyncSession = Depends(get_db)
) -> User:
    """Get the current authenticated user using JWT decode workaround."""
    # Extract token from Authorization header
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Missing or invalid authorization header"
        )
    
    token = auth_header.split(" ")[1]
    
    try:
        # Decode JWT token
        header_encoded, payload_encoded, signature_encoded = token.split('.')
        payload_decoded = base64.b64decode(payload_encoded + '==').decode('utf-8')
        payload = json.loads(payload_decoded)
        
        # Extract user ID from payload
        user_id_str = payload.get("sub")
        if not user_id_str:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID"
            )
        
        user_id = uuid.UUID(user_id_str)
        
        # Load user from database
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        return user
        
    except (ValueError, json.JSONDecodeError, IndexError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token format"
        )


async def get_current_active_user(
    user: User = Depends(get_current_user)
) -> User:
    """Get the current active user."""
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return user


async def get_current_system_owner(
    user: User = Depends(get_current_user)
) -> User:
    """Get the current user if they are a system owner."""
    if user.role != UserRole.SYSTEM_OWNER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="System owner access required"
        )
    return user


async def get_current_admin_or_system_owner(
    user: User = Depends(get_current_user)
) -> User:
    """Get the current user if they are an admin or system owner."""
    if user.role not in (UserRole.ADMIN, UserRole.SYSTEM_OWNER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin or system owner access required"
        )
    return user


async def get_current_tenant_user(
    user: User = Depends(get_current_user),
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
    user: User = Depends(get_current_user)
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
