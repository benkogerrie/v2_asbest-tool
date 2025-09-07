#!/usr/bin/env python3
"""
Test script to debug tenant admin S. Jansen report visibility issue.
"""

import asyncio
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import get_async_session_local
from app.models.user import User, UserRole
from app.models.tenant import Tenant
from app.models.report import Report
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

BASE_URL = 'https://v2asbest-tool-production.up.railway.app'

async def debug_tenant_admin_reports():
    """Debug why tenant admin S. Jansen doesn't see reports."""
    
    async with get_async_session_local() as session:
        print("🔍 Debugging tenant admin S. Jansen report visibility...")
        
        # 1. Find S. Jansen user
        result = await session.execute(
            select(User).where(User.first_name == 'S.').where(User.last_name == 'Jansen')
        )
        user = result.scalar_one_or_none()
        
        if not user:
            print("❌ User S. Jansen not found!")
            return
        
        print(f"✅ Found user: {user.first_name} {user.last_name}")
        print(f"   - Email: {user.email}")
        print(f"   - Role: {user.role}")
        print(f"   - Tenant ID: {user.tenant_id}")
        print(f"   - Is Active: {user.is_active}")
        
        # 2. Check tenant
        if user.tenant_id:
            result = await session.execute(
                select(Tenant).where(Tenant.id == user.tenant_id)
            )
            tenant = result.scalar_one_or_none()
            
            if tenant:
                print(f"✅ Found tenant: {tenant.name}")
                print(f"   - Tenant ID: {tenant.id}")
                print(f"   - Is Active: {tenant.is_active}")
            else:
                print("❌ Tenant not found!")
                return
        else:
            print("❌ User has no tenant_id!")
            return
        
        # 3. Check reports for this tenant
        result = await session.execute(
            select(func.count(Report.id)).where(Report.tenant_id == user.tenant_id)
        )
        total_reports = result.scalar()
        print(f"📊 Total reports for tenant: {total_reports}")
        
        # 4. Check reports by status
        for status in ['PROCESSING', 'DONE', 'FAILED', 'DELETED_SOFT']:
            result = await session.execute(
                select(func.count(Report.id)).where(
                    Report.tenant_id == user.tenant_id,
                    Report.status == status
                )
            )
            count = result.scalar()
            print(f"   - {status}: {count}")
        
        # 5. Get detailed report info
        result = await session.execute(
            select(Report).where(Report.tenant_id == user.tenant_id).limit(5)
        )
        reports = result.scalars().all()
        
        print(f"\n📋 Recent reports for tenant:")
        for report in reports:
            print(f"   - {report.filename} (Status: {report.status}, Uploaded: {report.uploaded_at})")
        
        # 6. Test the exact query that the API uses
        print(f"\n🔍 Testing API query logic...")
        
        # This is the exact logic from ReportService.get_reports_with_filters
        if user.role == UserRole.SYSTEM_OWNER:
            query = select(Report).options(selectinload(Report.tenant))
        else:
            query = select(Report)
        
        # Apply RBAC filters (this is the key part!)
        if user.role == UserRole.SYSTEM_OWNER:
            # SYSTEM_OWNER can see all reports
            pass
        else:
            # USER/ADMIN can only see reports from their tenant, excluding soft-deleted
            from sqlalchemy import and_
            from app.models.report import ReportStatus
            query = query.where(
                and_(
                    Report.tenant_id == user.tenant_id,
                    Report.status != ReportStatus.DELETED_SOFT
                )
            )
        
        # Execute the filtered query
        result = await session.execute(query)
        filtered_reports = result.scalars().all()
        
        print(f"📊 Reports visible to user after RBAC filtering: {len(filtered_reports)}")
        
        for report in filtered_reports[:5]:  # Show first 5
            print(f"   - {report.filename} (Status: {report.status}, Tenant: {report.tenant_id})")
        
        # 7. Check if there are any users with ADMIN role in this tenant
        result = await session.execute(
            select(User).where(
                User.tenant_id == user.tenant_id,
                User.role == UserRole.ADMIN
            )
        )
        admin_users = result.scalars().all()
        
        print(f"\n👥 Admin users in tenant: {len(admin_users)}")
        for admin in admin_users:
            print(f"   - {admin.first_name} {admin.last_name} ({admin.email})")

if __name__ == "__main__":
    asyncio.run(debug_tenant_admin_reports())
