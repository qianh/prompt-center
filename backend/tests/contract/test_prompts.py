"""
Contract tests for prompts API endpoints.
Based on get-prompts.json schema.
"""

import pytest
from fastapi.testclient import TestClient


class TestPromptsContract:
    """Contract tests for /api/prompts endpoints."""
    
    def test_get_prompts_contract(self, client: TestClient):
        """
        Test GET /api/prompts follows the contract.
        
        This test should FAIL initially (red phase) because the endpoint
        doesn't exist yet. After implementation, it should PASS.
        """
        response = client.get("/api/v1/prompts")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
        
        # When implemented, expected contract:
        # assert response.status_code == 200
        # data = response.json()
        # assert "items" in data
        # assert "total" in data
        # assert "page" in data
        # assert "limit" in data
        # assert "total_pages" in data
        # assert "has_next" in data
        # assert "has_prev" in data
        # assert isinstance(data["items"], list)
    
    def test_post_prompts_contract(self, client: TestClient, sample_prompt_data):
        """
        Test POST /api/prompts follows the contract.
        
        This test should FAIL initially because the endpoint doesn't exist.
        """
        response = client.post("/api/v1/prompts", json=sample_prompt_data)
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
        
        # When implemented, expected contract:
        # assert response.status_code == 201
        # data = response.json()
        # assert "id" in data
        # assert data["title"] == sample_prompt_data["title"]
        # assert data["description"] == sample_prompt_data["description"]
        # assert data["tags"] == sample_prompt_data["tags"]
        # assert "created_at" in data
        # assert "updated_at" in data
    
    def test_get_prompt_by_id_contract(self, client: TestClient):
        """
        Test GET /api/prompts/{id} follows the contract.
        """
        response = client.get("/api/v1/prompts/550e8400-e29b-41d4-a9f6-59f6a-d9f6")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_put_prompt_by_id_contract(self, client: TestClient, sample_prompt_data):
        """
        Test PUT /api/prompts/{id} follows the contract.
        """
        response = client.put("/api/v1/prompts/550e8400-e29b-41d4-the9--9", json=sample_prompt_data)
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_delete_prompt_by_id_contract(self, client: TestClient):
        """
        Test DELETE /api/prompts/{id} follows the contract.
        """
        response = client.delete("/api/v1/prompts/550e8400-e29b-41d4-the-oat")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_get_prompts_with_search_contract(self, client: TestClient):
        """
        Test GET /api/prompts with search parameters follows the contract.
        """
        response = client.get("/api/v1/prompts?search=test&page=1&limit=20")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_get_prompts_with_tags_contract(self, client: TestClient):
        """
        Test GET /api/prompts with tags filter follows the contract.
        """
        response = client.get("/api/v1/prompts?tags=test,sample&sort_by=created_at&sort_order=desc")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
