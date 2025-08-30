from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.auth.dependencies import current_system_owner, current_tenant_admin, get_user_tenant
from app.auth.auth import fastapi_users, auth_backend

router = APIRouter(prefix="/users", tags=["users"])

# Note: FastAPI Users routes are included in main.py to avoid conflicts


@router.get("/", response_model=List[UserRead])
async def list_users(
    current_user: User = Depends(current_tenant_admin),
    session: AsyncSession = Depends(get_db)
):
    """List users based on role and tenant."""
    if current_user.role == UserRole.SYSTEM_OWNER:
        # System owner sees all users
        result = await session.execute(select(User))
        users = result.scalars().all()
    else:
        # Tenant admin sees only users from their tenant
        result = await session.execute(
            select(User).where(User.tenant_id == current_user.tenant_id)
        )
        users = result.scalars().all()
    
    return users


@router.get("/me", response_model=UserRead)
async def get_current_user(
    current_user: User = Depends(current_tenant_admin)
):
    """Get current user information."""
    return current_user


@router.post("/", response_model=UserRead)
async def create_user(
    user_data: UserCreate,
    current_user: User = Depends(current_tenant_admin),
    session: AsyncSession = Depends(get_db)
):
    """Create a new user."""
    # Check if user can create users in this tenant
    if current_user.role == UserRole.SYSTEM_OWNER:
        # System owner can create users in any tenant or without tenant
        pass
    else:
        # Tenant admin can only create users in their own tenant
        if user_data.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Can only create users in your own tenant"
            )
        # Tenant admin cannot create system owners
        if user_data.role == UserRole.SYSTEM_OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot create system owners"
            )
    
    # Create user using FastAPI Users
    from app.auth.auth import get_user_manager
    user_manager = await anext(get_user_manager(session))
    
    user = await user_manager.create(user_data)
    return user


@router.get("/{user_id}", response_model=UserRead)
async def get_user(
    user_id: str,
    current_user: User = Depends(current_tenant_admin),
    session: AsyncSession = Depends(get_db)
):
    """Get a specific user."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access rights
    if current_user.role == UserRole.SYSTEM_OWNER:
        # System owner can see all users
        pass
    else:
        # Tenant admin can only see users from their tenant
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
    
    return user


@router.put("/{user_id}", response_model=UserRead)
async def update_user(
    user_id: str,
    user_data: UserUpdate,
    current_user: User = Depends(current_tenant_admin),
    session: AsyncSession = Depends(get_db)
):
    """Update a user."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access rights
    if current_user.role == UserRole.SYSTEM_OWNER:
        # System owner can update all users
        pass
    else:
        # Tenant admin can only update users from their tenant
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Tenant admin cannot update to system owner
        if user_data.role == UserRole.SYSTEM_OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot assign system owner role"
            )
    
    # Update user
    update_data = user_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    
    await session.commit()
    await session.refresh(user)
    return user


@router.delete("/{user_id}")
async def delete_user(
    user_id: str,
    current_user: User = Depends(current_tenant_admin),
    session: AsyncSession = Depends(get_db)
):
    """Delete a user."""
    result = await session.execute(
        select(User).where(User.id == user_id)
    )
    user = result.scalar_one_or_none()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Check access rights
    if current_user.role == UserRole.SYSTEM_OWNER:
        # System owner can delete all users
        pass
    else:
        # Tenant admin can only delete users from their tenant
        if user.tenant_id != current_user.tenant_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied"
            )
        # Tenant admin cannot delete system owners
        if user.role == UserRole.SYSTEM_OWNER:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot delete system owners"
            )
    
    await session.delete(user)
    await session.commit()
    
    return {"message": "User deleted successfully"}
