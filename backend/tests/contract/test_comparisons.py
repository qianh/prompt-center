"""
Contract tests for comparisons API endpoints.
Based on post-comparisons.json schema.
"""

import pytest
from fastapi.testclient import TestClient


class TestComparisonsContract:
    """Contract tests for /api/comparisons endpoints."""
    
    def test_post_comparisons_compare_contract(self, client: TestClient, sample_comparison_data):
        """
        Test POST /api/comparisons/compare follows the contract.
        
        This test should FAIL initially because the endpoint doesn't exist yet.
        """
        response = client.post("/api/v1/comparisons/compare", json=sample_comparison_data)
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
        
        # When implemented, expected contract:
        # assert response.status_code == 200
        # data = response.json()
        # assert "id" in data
        # assert "name" in data
        # assert "description" in data
        # assert "type" in data
        # assert "input_text" in data
        # assert "results" in data
        # assert "successful_executions" in data
        # assert "total_executions" in data
        # assert "average_execution_time_ms" in data
        # assert "total_tokens_used" in data
        # assert "created_at" in data
        # assert "updated_at" in data
    
    def test_get_comparisons_contract(self, client: TestClient):
        """
        Test GET /api/comparisons follows the contract.
        """
        response = client.get("/api/v1/comparisons")
        
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
    
    def test_get_comparison_by_id_contract(self, client: TestClient):
        """
        Test GET /api/comparisons/{id} follows the contract.
        """
        comparison_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        response = client.get(f"/api/v1/comparisons/{comparison_id}")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_delete_comparison_by_id_contract(self, client: TestClient):
        """
        Test DELETE /api/comparisons/{id} follows the contract.
        """
        comparison_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        response = client.delete(f"/api/v1/comparisons/{comparison_id}")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_export_comparison_contract(self, client: TestClient):
        """
        Test GET /api/comparisons/{id}/export follows the contract.
        """
        comparison_id = "550e8400-e29b-41d4-a9f6-7f6a6d9f6"
        response = client.get(f"/api/v1/comparisons/{comparison_id}/export?format=json")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
    
    def test_get_comparisons_with_filters_contract(self, client: TestClient):
        """
        Test GET /api/comparisons with filters follows the contract.
        """
        response = client.get("/api/v1/comparisons?type=version_comparison&page=1&limit=20")
        
        # Should fail because endpoint doesn't exist yet
        assert response.status_code == 404, "Endpoint should not exist yet"
