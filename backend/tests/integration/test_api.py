"""
Basic API integration tests.
"""
import pytest


@pytest.mark.integration
def test_root_endpoint(client):
    """Test the root endpoint returns correct structure."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "name" in data
    assert "version" in data
    assert "status" in data
    assert data["status"] == "healthy"


@pytest.mark.integration
def test_health_check(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert "status" in data
    assert data["status"] == "healthy"
    assert "api" in data
    assert data["api"] == "operational"


@pytest.mark.integration
class TestHRPEndpoints:
    """Integration tests for HRP endpoints."""
    
    def test_correlation_endpoint_valid_request(self, client):
        """Test correlation endpoint with valid request."""
        payload = {
            "tickers": ["AAPL", "MSFT", "GOOGL"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        
        response = client.post("/hrp/correlation", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure
        assert "tickers" in data
        assert "correlation_matrix" in data
        assert "start_date" in data
        assert "end_date" in data
        assert "data_points" in data
        
        # Check data types
        assert isinstance(data["tickers"], list)
        assert isinstance(data["correlation_matrix"], list)
        assert isinstance(data["data_points"], int)
        
        # Check we have at least 2 tickers
        assert len(data["tickers"]) >= 2
        
        # Check correlation matrix is square
        assert len(data["correlation_matrix"]) == len(data["tickers"])
        assert len(data["correlation_matrix"][0]) == len(data["tickers"])
    
    def test_correlation_endpoint_empty_tickers(self, client):
        """Test correlation endpoint with empty tickers list."""
        payload = {
            "tickers": [],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        
        response = client.post("/hrp/correlation", json=payload)
        
        # Should return 422 (validation error)
        assert response.status_code == 422
    
    def test_correlation_endpoint_single_ticker(self, client):
        """Test correlation endpoint with only one ticker."""
        payload = {
            "tickers": ["AAPL"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        
        response = client.post("/hrp/correlation", json=payload)
        
        # Should return 422 (need at least 2 tickers)
        assert response.status_code == 422
    
    def test_correlation_endpoint_invalid_date_format(self, client):
        """Test correlation endpoint with invalid date format."""
        payload = {
            "tickers": ["AAPL", "MSFT"],
            "start_date": "01-01-2023",  # Wrong format
            "end_date": "2023-01-31"
        }
        
        response = client.post("/hrp/correlation", json=payload)
        
        # Should return 422 (validation error)
        assert response.status_code == 422
    
    def test_correlation_endpoint_duplicate_tickers(self, client):
        """Test correlation endpoint with duplicate tickers."""
        payload = {
            "tickers": ["AAPL", "AAPL", "MSFT"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31"
        }
        
        response = client.post("/hrp/correlation", json=payload)
        
        # Should succeed - duplicates should be removed
        assert response.status_code == 200
        data = response.json()
        
        # Should only have 2 unique tickers
        assert len(data["tickers"]) == 2
    
    def test_hrp_analyze_endpoint_valid_request(self, client):
        """Test HRP analyze endpoint with valid request."""
        payload = {
            "tickers": ["AAPL", "MSFT", "GOOGL"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "linkage_method": "ward"
        }
        
        response = client.post("/hrp/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Check response structure (matches HRPResponse model)
        assert "ordered_tickers" in data
        assert "dendrogram_data" in data
        assert "heatmap_data" in data
        assert "cluster_leaf_map" in data
        assert "linkage_method" in data
        assert "data_points" in data
        
        # Check data types
        assert isinstance(data["ordered_tickers"], list)
        assert isinstance(data["dendrogram_data"], dict)
        assert isinstance(data["heatmap_data"], list)
        assert isinstance(data["cluster_leaf_map"], dict)
        assert isinstance(data["linkage_method"], str)
        assert isinstance(data["data_points"], int)
        
        # Check linkage method
        assert data["linkage_method"] == "ward"
        
        # Check we have at least 2 tickers
        assert len(data["ordered_tickers"]) >= 2
        
        # Check dendrogram data has required fields
        assert "name" in data["dendrogram_data"]
        assert "height" in data["dendrogram_data"]
        
        # Check heatmap data structure
        assert len(data["heatmap_data"]) > 0
        heatmap_item = data["heatmap_data"][0]
        assert "x" in heatmap_item
        assert "y" in heatmap_item
        assert "value" in heatmap_item
        
        # Check cluster_leaf_map structure
        assert len(data["cluster_leaf_map"]) > 0
        # All values should be lists of tickers
        for cluster_id, tickers in data["cluster_leaf_map"].items():
            assert isinstance(tickers, list)
            assert len(tickers) > 0
    
    def test_hrp_analyze_endpoint_different_linkage_methods(self, client):
        """Test HRP analyze endpoint with different linkage methods."""
        linkage_methods = ["single", "complete", "average", "ward"]
        
        for method in linkage_methods:
            payload = {
                "tickers": ["AAPL", "MSFT", "GOOGL"],
                "start_date": "2023-01-01",
                "end_date": "2023-01-31",
                "linkage_method": method
            }
            
            response = client.post("/hrp/analyze", json=payload)
            
            assert response.status_code == 200
            data = response.json()
            assert data["linkage_method"] == method
    
    def test_hrp_analyze_endpoint_invalid_linkage_method(self, client):
        """Test HRP analyze endpoint with invalid linkage method."""
        payload = {
            "tickers": ["AAPL", "MSFT", "GOOGL"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "linkage_method": "invalid_method"
        }
        
        response = client.post("/hrp/analyze", json=payload)
        
        # Should return 422 (validation error)
        assert response.status_code == 422
    
    def test_hrp_analyze_endpoint_empty_tickers(self, client):
        """Test HRP analyze endpoint with empty tickers list."""
        payload = {
            "tickers": [],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "linkage_method": "ward"
        }
        
        response = client.post("/hrp/analyze", json=payload)
        
        # Should return 422 (validation error)
        assert response.status_code == 422
    
    def test_hrp_analyze_endpoint_single_ticker(self, client):
        """Test HRP analyze endpoint with only one ticker."""
        payload = {
            "tickers": ["AAPL"],
            "start_date": "2023-01-01",
            "end_date": "2023-01-31",
            "linkage_method": "ward"
        }
        
        response = client.post("/hrp/analyze", json=payload)
        
        # Should return 422 (need at least 2 tickers for correlation/clustering)
        assert response.status_code == 422
