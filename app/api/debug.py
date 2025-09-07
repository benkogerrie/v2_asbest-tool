"""
Debug endpoints to isolate authentication issues.
"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.models.user import User
from app.auth.auth import fastapi_users

router = APIRouter(prefix="/debug", tags=["debug"])

@router.get("/test-auth-1")
async def test_auth_1(
    current_user: User = Depends(fastapi_users.current_user(active=True))
):
    """Test direct FastAPI Users dependency."""
    return {
        "status": "success",
        "method": "direct_fastapi_users",
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "user_role": current_user.role
    }

@router.get("/test-auth-2")
async def test_auth_2(
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(get_db)
):
    """Test FastAPI Users dependency with database session."""
    return {
        "status": "success",
        "method": "fastapi_users_with_db",
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "user_role": current_user.role,
        "session_active": session is not None
    }

@router.get("/test-auth-3")
async def test_auth_3(
    current_user: User = Depends(fastapi_users.current_user(active=True)),
    session: AsyncSession = Depends(get_db)
):
    """Test with simple database query."""
    from sqlalchemy import select
    from app.models.report import Report
    
    # Simple count query
    result = await session.execute(select(Report.id))
    count = len(result.fetchall())
    
    return {
        "status": "success",
        "method": "fastapi_users_with_db_query",
        "user_id": str(current_user.id),
        "user_email": current_user.email,
        "user_role": current_user.role,
        "report_count": count
    }
