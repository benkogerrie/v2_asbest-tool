from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.schemas.tenant import TenantCreate, TenantRead, TenantUpdate, TenantWithAdminCreate, TenantWithAdminResponse
from app.auth.dependencies import get_current_system_owner, get_current_tenant_user

router = APIRouter(prefix="/tenants", tags=["tenants"])


@router.get("/", response_model=List[TenantRead])
async def list_tenants(
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """List all tenants (system owner only)."""
    result = await session.execute(select(Tenant))
    tenants = result.scalars().all()
    return tenants


@router.get("/my", response_model=TenantRead)
async def get_my_tenant(
    current_user: User = Depends(get_current_tenant_user),
    session: AsyncSession = Depends(get_db)
):
    """Get current user's tenant."""
    if current_user.role == UserRole.SYSTEM_OWNER:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="System owner has no tenant"
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


@router.post("/", response_model=TenantRead)
async def create_tenant(
    tenant_data: TenantCreate,
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Create a new tenant (system owner only)."""
    tenant = Tenant(**tenant_data.model_dump())
    session.add(tenant)
    await session.commit()
    await session.refresh(tenant)
    return tenant


@router.post("/with-admin", response_model=TenantWithAdminResponse)
async def create_tenant_with_admin(
    data: TenantWithAdminCreate,
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Create a new tenant with an admin user (system owner only)."""
    try:
        from app.services.email import email_service
        from app.auth.auth import get_user_manager
        
        # Create tenant
        tenant = Tenant(**data.tenant.model_dump())
        session.add(tenant)
        await session.commit()
        await session.refresh(tenant)
        
        # Generate temporary password
        temp_password = email_service.generate_temp_password()
        
        # Create admin user using FastAPI Users schema
        from fastapi_users import schemas
        
        # Prepare admin data with all required fields
        admin_data = {
            'email': data.admin.get('email', ''),
            'password': temp_password,
            'first_name': data.admin.get('first_name', ''),
            'last_name': data.admin.get('last_name', ''),
            'role': UserRole.ADMIN,
            'tenant_id': tenant.id,
            'phone': data.admin.get('phone'),
            'department': data.admin.get('department'),
            'job_title': data.admin.get('job_title'),
            'employee_id': data.admin.get('employee_id')
        }
        
        # Use FastAPI Users BaseUserCreate schema
        admin_create = schemas.BaseUserCreate(**admin_data)
        
        # Create user using FastAPI Users
        from app.auth.auth import get_user_db
        user_db = await anext(get_user_db(session))
        user_manager = await anext(get_user_manager(user_db))
        admin_user = await user_manager.create(admin_create)
        
        # Send invitation email
        admin_name = f"{admin_user.first_name} {admin_user.last_name}"
        invitation_sent = email_service.send_tenant_admin_invitation(
            admin_user.email, 
            admin_name, 
            tenant.name, 
            temp_password
        )
        
        # Prepare response
        admin_info = {
            "id": str(admin_user.id),
            "email": admin_user.email,
            "first_name": admin_user.first_name,
            "last_name": admin_user.last_name,
            "role": admin_user.role,
            "tenant_id": str(admin_user.tenant_id),
            "is_active": admin_user.is_active,
            "is_verified": admin_user.is_verified,
            "created_at": admin_user.created_at.isoformat()
        }
        
        return TenantWithAdminResponse(
            tenant=tenant,
            admin=admin_info,
            temp_password=temp_password,
            invitation_sent=invitation_sent
        )
        
    except Exception as e:
        # Rollback tenant creation if user creation fails
        await session.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to create tenant with admin: {str(e)}"
        )


@router.get("/{tenant_id}", response_model=TenantRead)
async def get_tenant(
    tenant_id: str,
    current_user: User = Depends(get_current_system_owner),
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
    current_user: User = Depends(get_current_system_owner),
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
    current_user: User = Depends(get_current_system_owner),
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
