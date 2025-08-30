
#!/usr/bin/env python3
"""
Seed script voor het aanmaken van initiële data.
"""
import asyncio
import uuid
from datetime import datetime, UTC
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.tenant import Tenant
from app.models.user import User, UserRole
from app.auth.auth import UserManager
from app.auth.auth import get_user_db


async def create_system_owner(session: AsyncSession) -> User:
    """Maak een system owner aan."""
    # Check if system owner already exists
    result = await session.execute(
        select(User).where(User.email == "system@asbest-tool.nl")
    )
    existing_user = result.scalar_one_or_none()
    
    if existing_user:
        print(f"✅ System owner bestaat al: {existing_user.email}")
        return existing_user
    
    # Create system owner directly
    system_owner = User(
        email="system@asbest-tool.nl",
        first_name="System",
        last_name="Owner",
        role=UserRole.SYSTEM_OWNER,
        tenant_id=None,
        is_active=True,
        is_superuser=True,
        is_verified=True,
        created_at=datetime.utcnow()
    )
    
    # Hash the password
    from app.auth.auth import UserManager
    user_manager = UserManager(None)  # We'll set the user_db later
    system_owner.hashed_password = user_manager.password_helper.hash("SystemOwner123!")
    
    session.add(system_owner)
    await session.commit()
    
    print(f"✅ System owner aangemaakt: {system_owner.email}")
    return system_owner


async def create_tenant_and_admin(session: AsyncSession) -> tuple[Tenant, User]:
    """Maak een tenant en tenant admin aan."""
    # Check if tenant already exists
    result = await session.execute(
        select(Tenant).where(Tenant.name == "Bedrijf Y")
    )
    existing_tenant = result.scalar_one_or_none()
    
    if existing_tenant:
        tenant = existing_tenant
        print(f"✅ Tenant bestaat al: {tenant.name}")
    else:
        # Maak tenant aan
        tenant = Tenant(
            id=uuid.uuid4(),
            name="Bedrijf Y",
            kvk="12345678",
            contact_email="admin@bedrijfy.nl",
            is_active=True,
            created_at=datetime.utcnow()
        )
        session.add(tenant)
        await session.commit()
        print(f"✅ Tenant aangemaakt: {tenant.name}")
    
    # Check if tenant admin already exists
    result = await session.execute(
        select(User).where(User.email == "admin@bedrijfy.nl")
    )
    existing_admin = result.scalar_one_or_none()
    
    if existing_admin:
        tenant_admin = existing_admin
        print(f"✅ Tenant admin bestaat al: {tenant_admin.email}")
    else:
        # Maak tenant admin aan
        from app.auth.auth import UserManager
        user_manager = UserManager(None)  # We'll set the user_db later
        
        tenant_admin = User(
            email="admin@bedrijfy.nl",
            first_name="Admin",
            last_name="Bedrijf Y",
            role=UserRole.ADMIN,
            tenant_id=tenant.id,
            is_active=True,
            is_superuser=False,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        # Hash the password
        tenant_admin.hashed_password = user_manager.password_helper.hash("Admin123!")
        
        session.add(tenant_admin)
        await session.commit()
        print(f"✅ Tenant admin aangemaakt: {tenant_admin.email}")
    
    return tenant, tenant_admin


async def main():
    """Hoofdfunctie voor het seeden van data."""
    print("🌱 Starten met seeden van initiële data...")
    
    async with AsyncSessionLocal() as session:
        try:
            # Maak system owner aan
            system_owner = await create_system_owner(session)
            
            # Maak tenant en tenant admin aan
            tenant, tenant_admin = await create_tenant_and_admin(session)
            
            print("\n🎉 Seeding voltooid!")
            print("\n📋 Aangemaakte accounts:")
            print(f"   System Owner: {system_owner.email} (wachtwoord: SystemOwner123!)")
            print(f"   Tenant Admin: {tenant_admin.email} (wachtwoord: Admin123!)")
            print(f"   Tenant: {tenant.name} (ID: {tenant.id})")
            
        except Exception as e:
            print(f"❌ Fout tijdens seeden: {e}")
            await session.rollback()
            raise


if __name__ == "__main__":
    asyncio.run(main())
