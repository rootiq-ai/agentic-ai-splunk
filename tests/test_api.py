"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, patch
from src.api.main import app

client = TestClient(app)

class TestAPIEndpoints:
    """Test cases for API endpoints."""
    
    def test_root_endpoint(self):
        """Test root endpoint."""
        response = client.get("/")
        assert response.status_code == 200
        assert "name" in response.json()
    
    def test_health_endpoint(self):
        """Test health endpoint."""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    @patch('src.api.routes.query.get_query_processor')
    def test_natural_language_query_success(self, mock_get_processor):
        """Test successful natural language query."""
        # Mock processor response
        mock_processor = Mock()
        mock_processor.process_natural_language_query.return_value = {
            "success": True,
            "question": "test question",
            "spl_query": "search index=main",
            "explanation": "test explanation",
            "confidence": "high",
            "results": [{"field": "value"}],
            "result_count": 1,
            "statistics": {"result_count": 1, "scan_count": 10, "run_duration": 1.0},
            "validation": {"valid": True, "query": "search index=main"},
            "processing_time": 1.5
        }
        mock_get_processor.return_value = mock_processor
        
        response = client.post(
            "/api/v1/query/natural",
            json={"question": "test question", "max_results": 100}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["question"] == "test question"
    
    @patch('src.api.routes.query.get_query_processor')
    def test_spl_query_success(self, mock_get_processor):
        """Test successful SPL query."""
        # Mock processor response
        mock_processor = Mock()
        mock_processor.execute_spl_query.return_value = {
            "success": True,
            "spl_query": "search index=main",
            "results": [{"field": "value"}],
            "result_count": 1,
            "statistics": {"result_count": 1, "scan_count": 10, "run_duration": 1.0},
            "validation": {"valid": True, "query": "search index=main"},
            "processing_time": 1.0
        }
        mock_get_processor.return_value = mock_processor
        
        response = client.post(
            "/api/v1/query/spl",
            json={"spl_query": "search index=main", "max_results": 100}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["spl_query"] == "search index=main"
    
    def test_invalid_natural_language_query(self):
        """Test invalid natural language query."""
        response = client.post(
            "/api/v1/query/natural",
            json={"question": "", "max_results": 100}
        )
        
        assert response.status_code == 422  # Pydantic validation error
    
    def test_invalid_spl_query(self):
        """Test invalid SPL query."""
        response = client.post(
            "/api/v1/query/spl",
            json={"spl_query": "invalid query", "max_results": 100}
        )
        
        assert response.status_code == 400
