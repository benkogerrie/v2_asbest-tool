import pytest
from httpx import AsyncClient


class TestHealth:
    """Test health endpoint functionaliteit."""
    
    async def test_health_endpoint(self, client: AsyncClient):
        """Test dat health endpoint werkt."""
        response = await client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "database" in data
        assert "timestamp" in data
    
    async def test_health_endpoint_structure(self, client: AsyncClient):
        """Test dat health endpoint de juiste structuur heeft."""
        response = await client.get("/healthz")
        
        data = response.json()
        assert isinstance(data["status"], str)
        assert isinstance(data["database"], str)
        assert isinstance(data["timestamp"], str)
    
    async def test_health_endpoint_accessible_without_auth(self, client: AsyncClient):
        """Test dat health endpoint toegankelijk is zonder authenticatie."""
        response = await client.get("/healthz")
        
        assert response.status_code == 200
