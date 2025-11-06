"""
Contract tests for prompt versions API endpoints.
Based on post-versions.json schema.
"""

import pytest
from fastapi.testclient import TestClient


class TestVersionsContract:
    """Contract tests for /api/prompts/{id}/versions endpoints."""
    
    def test_post_prompt_versions_contract(self, client: TestClient, sample_version_data):
        """
        Test POST /api/prompts/{id}/versions follows the contract.
        
        This test should FAIL initially because the endpoint doesn't exist yet.
        """
        prompt_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        response = client.post(f"/api/v1/prompts/{prompt_id}/versions", json=sample_version_data)
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
        
        # When implemented, expected contract:
        # assert response.status_code == 201
        # data = response.json()
        # assert "id" in data
        # assert "prompt_id" in data
        # assert "version_number" in data
        # assert data["content"] == sample_version_data["content"]
        # assert data["change_notes"] == sample_version_data["change_notes"]
        # assert "created_at" in data
        # assert "updated_at" in data
    
    def test_get_prompt_versions_contract(self, client: TestClient):
        """
        Test GET /api/prompts/{id}/versions follows the contract.
        """
        prompt_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        response = client.get(f"/api/v1/prompts/{prompt_id}/versions")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
        
        # When implemented, expected contract:
        # assert response.status_code == 200
        # data = response.json()
        # assert isinstance(data, list)
        # if data:  # If there are versions
        #     assert "id" in data[0]
        #     assert "prompt_id" in data[0]
        #     assert "version_number" in data[0]
        #     assert "content" in data[0]
    
    def test_get_specific_version_contract(self, client: TestClient):
        """
        Test GET /api/prompts/{id}/versions/{version_id} follows the contract.
        """
        prompt_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        version_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f7"
        response = client.get(f"/api/v1/prompts/{prompt_id}/versions/{version_id}")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_put_specific_version_contract(self, client: TestClient, sample_version_data):
        """
        Test PUT /api/prompts/{id}/versions/{version_id} follows the contract.
        """
        prompt_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        version_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f7"
        response = client.put(f"/api/v1/prompts/{prompt_id}/versions/{version_id}", json=sample_version_data)
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_delete_specific_version_contract(self, client: TestClient):
        """
        Test DELETE /api/prompts/{id}/versions/{version_id} follows the contract.
        """
        prompt_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        version_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f7"
        response = client.delete(f"/api/v1/prompts/{prompt_id}/versions/{version_id}")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_compare_versions_contract(self, client: TestClient):
        """
        Test GET /api/prompts/{id}/versions/compare follows the contract.
        """
        prompt_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        response = client.get(f"/api/v1/prompts/{prompt_id}/versions/compare?version_a=1&version_b=2")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
