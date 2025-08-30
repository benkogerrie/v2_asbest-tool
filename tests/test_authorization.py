import pytest
from httpx import AsyncClient


class TestAuthorization:
    """Test autorisatie functionaliteit."""
    
    async def test_system_owner_sees_all_tenants(self, client: AsyncClient, system_owner, tenant):
        """Test dat system owner alle tenants kan zien."""
        # Login als system owner
        login_response = await client.post(
            "/users/auth/jwt/login",
            data={
                "username": "system@test.nl",
                "password": "SystemOwner123!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Test tenants endpoint
        response = await client.get(
            "/tenants/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 1  # Minimaal de test tenant
    
    async def test_system_owner_sees_all_users(self, client: AsyncClient, system_owner, tenant_admin, tenant_user):
        """Test dat system owner alle users kan zien."""
        # Login als system owner
        login_response = await client.post(
            "/users/auth/jwt/login",
            data={
                "username": "system@test.nl",
                "password": "SystemOwner123!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Test users endpoint
        response = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert len(data) >= 3  # system_owner, tenant_admin, tenant_user
    
    async def test_tenant_admin_only_sees_own_tenant_users(self, client: AsyncClient, tenant_admin, tenant_user):
        """Test dat tenant admin alleen users van eigen tenant kan zien."""
        # Login als tenant admin
        login_response = await client.post(
            "/users/auth/jwt/login",
            data={
                "username": "admin@testbedrijf.nl",
                "password": "Admin123!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Test users endpoint
        response = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Tenant admin zou alleen users van eigen tenant moeten zien
        for user in data:
            assert user["tenant_id"] == str(tenant_admin.tenant_id)
    
    async def test_tenant_admin_cannot_access_tenants_list(self, client: AsyncClient, tenant_admin):
        """Test dat tenant admin geen toegang heeft tot tenants lijst."""
        # Login als tenant admin
        login_response = await client.post(
            "/users/auth/jwt/login",
            data={
                "username": "admin@testbedrijf.nl",
                "password": "Admin123!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Test tenants endpoint
        response = await client.get(
            "/tenants/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    async def test_tenant_admin_can_access_own_tenant(self, client: AsyncClient, tenant_admin):
        """Test dat tenant admin toegang heeft tot eigen tenant."""
        # Login als tenant admin
        login_response = await client.post(
            "/users/auth/jwt/login",
            data={
                "username": "admin@testbedrijf.nl",
                "password": "Admin123!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Test my tenant endpoint
        response = await client.get(
            "/tenants/my",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Test Bedrijf"
    
    async def test_tenant_user_cannot_access_admin_endpoints(self, client: AsyncClient, tenant_user):
        """Test dat gewone tenant user geen toegang heeft tot admin endpoints."""
        # Login als tenant user
        login_response = await client.post(
            "/users/auth/jwt/login",
            data={
                "username": "user@testbedrijf.nl",
                "password": "User123!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Test users endpoint (admin only)
        response = await client.get(
            "/users/",
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
    
    async def test_tenant_admin_cannot_create_system_owner(self, client: AsyncClient, tenant_admin, tenant):
        """Test dat tenant admin geen system owner kan aanmaken."""
        # Login als tenant admin
        login_response = await client.post(
            "/users/auth/jwt/login",
            data={
                "username": "admin@testbedrijf.nl",
                "password": "Admin123!"
            }
        )
        token = login_response.json()["access_token"]
        
        # Probeer system owner aan te maken
        user_data = {
            "email": "newadmin@test.nl",
            "password": "NewAdmin123!",
            "first_name": "New",
            "last_name": "Admin",
            "role": "SYSTEM_OWNER",
            "tenant_id": str(tenant.id)
        }
        
        response = await client.post(
            "/users/",
            json=user_data,
            headers={"Authorization": f"Bearer {token}"}
        )
        
        assert response.status_code == 403
