#!/usr/bin/env python3
"""
Test script to debug ReportService issues.
"""
import asyncio
import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'app'))

from app.services.reports import ReportService
from app.database import get_async_session_local
from app.models.user import User, UserRole
import uuid

async def test_report_service():
    """Test the ReportService to find the issue."""
    print("🔍 Testing ReportService...")
    
    try:
        # Get a database session
        async with get_async_session_local() as session:
            # Create a mock user
            mock_user = User(
                id=uuid.uuid4(),
                email="test@example.com",
                role=UserRole.SYSTEM_OWNER,
                tenant_id=None,
                first_name="Test",
                last_name="User",
                is_active=True,
                is_superuser=True,
                is_verified=True
            )
            
            # Create ReportService instance
            service = ReportService(session)
            
            # Test with a known report ID
            report_id = "456ef225-96c9-4e09-8331-3a0cd1abf78c"
            
            print(f"Testing get_report_detail with ID: {report_id}")
            
            # Try to get report detail
            result = await service.get_report_detail(report_id, mock_user)
            
            if result:
                print("✅ ReportService works!")
                print(f"Report ID: {result.id}")
                print(f"Filename: {result.filename}")
                print(f"Status: {result.status}")
            else:
                print("❌ ReportService returned None")
                
    except Exception as e:
        print(f"❌ Error in ReportService: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_report_service())
