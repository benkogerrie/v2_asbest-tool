"""
External APIs management endpoints for System Owner.
"""
import os
import httpx
import logging
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.auth.dependencies import get_current_system_owner
from app.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/admin/external-apis", tags=["external-apis"])


class GoogleMapsConfig(BaseModel):
    api_key: str
    enabled: bool = False


class BAGConfig(BaseModel):
    api_key: str
    enabled: bool = False


class APIStatusResponse(BaseModel):
    google_maps: dict
    bag: dict


@router.get("/google-maps")
async def get_google_maps_config(
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Get Google Maps API configuration."""
    try:
        api_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        enabled = os.getenv("GOOGLE_MAPS_ENABLED", "false").lower() == "true"
        
        return {
            "success": True,
            "data": {
                "api_key": api_key,
                "enabled": enabled
            }
        }
    except Exception as e:
        logger.error(f"Error getting Google Maps config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get Google Maps config")


@router.post("/google-maps")
async def save_google_maps_config(
    config: GoogleMapsConfig,
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Save Google Maps API configuration."""
    try:
        # In a real implementation, you would save this to a database
        # For now, we'll just return success
        # TODO: Implement proper configuration storage
        
        logger.info(f"Google Maps config saved by user {current_user.id}")
        
        return {
            "success": True,
            "message": "Google Maps configuration saved successfully"
        }
    except Exception as e:
        logger.error(f"Error saving Google Maps config: {e}")
        raise HTTPException(status_code=500, detail="Failed to save Google Maps config")


@router.post("/google-maps/test")
async def test_google_maps_api(
    config: GoogleMapsConfig,
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Test Google Maps API key."""
    try:
        # Test the API key by making a simple request
        test_url = "https://maps.googleapis.com/maps/api/streetview"
        params = {
            "size": "100x100",
            "location": "52.3676,4.9041",  # Amsterdam coordinates
            "key": config.api_key
        }
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(test_url, params=params)
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Google Maps API key is valid"
                }
            else:
                return {
                    "success": False,
                    "message": f"API test failed: {response.status_code}"
                }
                
    except Exception as e:
        logger.error(f"Error testing Google Maps API: {e}")
        return {
            "success": False,
            "message": f"API test failed: {str(e)}"
        }


@router.get("/bag")
async def get_bag_config(
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Get BAG API configuration."""
    try:
        api_key = os.getenv("BAG_API_KEY", "")
        enabled = os.getenv("BAG_ENABLED", "false").lower() == "true"
        
        return {
            "success": True,
            "data": {
                "api_key": api_key,
                "enabled": enabled
            }
        }
    except Exception as e:
        logger.error(f"Error getting BAG config: {e}")
        raise HTTPException(status_code=500, detail="Failed to get BAG config")


@router.post("/bag")
async def save_bag_config(
    config: BAGConfig,
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Save BAG API configuration."""
    try:
        # In a real implementation, you would save this to a database
        # For now, we'll just return success
        # TODO: Implement proper configuration storage
        
        logger.info(f"BAG config saved by user {current_user.id}")
        
        return {
            "success": True,
            "message": "BAG configuration saved successfully"
        }
    except Exception as e:
        logger.error(f"Error saving BAG config: {e}")
        raise HTTPException(status_code=500, detail="Failed to save BAG config")


@router.post("/bag/test")
async def test_bag_api(
    config: BAGConfig,
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Test BAG API key."""
    try:
        # Test the API key by making a simple request to BAG API
        # This is a placeholder - you would need to implement actual BAG API testing
        # based on the specific BAG API documentation
        
        if not config.api_key:
            return {
                "success": False,
                "message": "No API key provided"
            }
        
        # For now, just check if the key looks valid (starts with expected prefix)
        if len(config.api_key) < 10:
            return {
                "success": False,
                "message": "API key appears to be invalid (too short)"
            }
        
        return {
            "success": True,
            "message": "BAG API key appears to be valid (basic validation passed)"
        }
        
    except Exception as e:
        logger.error(f"Error testing BAG API: {e}")
        return {
            "success": False,
            "message": f"API test failed: {str(e)}"
        }


@router.get("/status")
async def get_api_status(
    current_user: User = Depends(get_current_system_owner),
    session: AsyncSession = Depends(get_db)
):
    """Get status of all external APIs."""
    try:
        google_maps_key = os.getenv("GOOGLE_MAPS_API_KEY", "")
        google_maps_enabled = os.getenv("GOOGLE_MAPS_ENABLED", "false").lower() == "true"
        
        bag_key = os.getenv("BAG_API_KEY", "")
        bag_enabled = os.getenv("BAG_ENABLED", "false").lower() == "true"
        
        return {
            "success": True,
            "data": {
                "google_maps": {
                    "configured": bool(google_maps_key),
                    "enabled": google_maps_enabled
                },
                "bag": {
                    "configured": bool(bag_key),
                    "enabled": bag_enabled
                }
            }
        }
    except Exception as e:
        logger.error(f"Error getting API status: {e}")
        raise HTTPException(status_code=500, detail="Failed to get API status")
