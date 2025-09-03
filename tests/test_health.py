import pytest


class TestHealth:
    """Test health endpoint functionaliteit."""
    
    def test_health_endpoint(self, client):
        """Test dat health endpoint werkt."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "message" in data
        assert "timestamp" in data
    
    def test_health_endpoint_structure(self, client):
        """Test dat health endpoint de juiste structuur heeft."""
        response = client.get("/healthz")
        
        data = response.json()
        assert isinstance(data["status"], str)
        assert isinstance(data["message"], str)
        assert isinstance(data["timestamp"], str)
    
    def test_health_endpoint_accessible_without_auth(self, client):
        """Test dat health endpoint toegankelijk is zonder authenticatie."""
        response = client.get("/healthz")
        
        assert response.status_code == 200
