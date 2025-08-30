from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.tenant import TenantCreate, TenantRead, TenantUpdate
from app.auth.dependencies import current_system_owner, get_user_tenant

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/", response_model=List[TenantRead])
async def list_tenants(
    current_user: User = Depends(current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """List all tenants (system owner only)."""
    result = await session.execute(select(Tenant))
    tenants = result.scalars().all()
    return tenants


@router.get("/my", response_model=TenantRead)
async def get_my_tenant(
    tenant: Tenant = Depends(get_user_tenant)
):
    """Get current user's tenant."""
    return tenant


@router.post("/", response_model=TenantRead)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Create a new tenant (system owner only)."""
    tenant = Tenant(**tenant_data.model_dump())
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    return tenant


@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant(
    tenant_id: str,
    current_user: User = Depends(current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Get a specific tenant (system owner only)."""
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    return tenant


@router.put("/{tenant_id}", response_model=TenantRead)
async def update_tenant(
    tenant_id: str,
    tenant_data: TenantUpdate,
    current_user: User = Depends(current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Update a tenant (system owner only)."""
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    update_data = tenant_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(tenant, field, value)
    
    await session.commit()
    await session.refresh(tenant)
    return tenant


@router.delete("/{tenant_id}")
async def delete_tenant(
    tenant_id: str,
    current_user: User = Depends(current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Delete a tenant (system owner only)."""
    result = await session.execute(
        select(Tenant).where(Tenant.id == tenant_id)
    )
    tenant = result.scalar_one_or_none()
    
    if not tenant:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Tenant not found"
        )
    
    await session.delete(tenant)
    await session.commit()
    
    return {"message": "Tenant deleted successfully"}
