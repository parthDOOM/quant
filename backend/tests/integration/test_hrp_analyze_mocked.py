"""
Integration tests for HRP analyze endpoint with mocked data.

These tests bypass the yfinance API to verify the integration between
correlation calculation and clustering works correctly.
"""
import pytest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock


@pytest.mark.integration
class TestHRPAnalyzeMocked:
    """Integration tests for HRP analysis with mocked data ingestion."""
    
    @patch('app.routers.hrp.get_correlation_data')
    def test_hrp_analyze_complete_pipeline_mocked(self, mock_get_correlation, client):
        """Test complete HRP analysis pipeline with mocked correlation data."""
        # Create synthetic correlation matrix
        tickers = ['AAPL', 'MSFT', 'GOOGL', 'AMZN']
        corr_matrix = pd.DataFrame([
            [1.00, 0.85, 0.72, 0.68],
            [0.85, 1.00, 0.75, 0.65],
            [0.72, 0.75, 1.00, 0.80],
            [0.68, 0.65, 0.80, 1.00]
        ], index=tickers, columns=tickers)
        
        # Mock the correlation data response
        mock_returns = pd.DataFrame(
            np.random.randn(100, 4),
            columns=tickers
        )
        mock_metadata = {
            'actual_tickers': tickers,
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'data_points': 100
        }
        mock_get_correlation.return_value = (mock_returns, corr_matrix, mock_metadata)
        
        # Make API request
        payload = {
            "tickers": tickers,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "linkage_method": "ward"
        }
        
        response = client.post("/hrp/analyze", json=payload)
        
        # Assert successful response
        assert response.status_code == 200
        data = response.json()
        
        # Validate response structure
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
        
        # Validate tickers - should be reordered but contain all original tickers
        assert set(data["ordered_tickers"]) == set(tickers)
        assert len(data["ordered_tickers"]) == 4
        
        # Validate linkage method
        assert data["linkage_method"] == "ward"
        
        # Validate dendrogram data structure
        tree = data["dendrogram_data"]
        assert "name" in tree
        assert isinstance(tree["name"], str)
        
        # Tree should have children (it's hierarchical)
        if "children" in tree:
            assert isinstance(tree["children"], list)
            assert len(tree["children"]) > 0
        
        # Validate heatmap data
        assert isinstance(data["heatmap_data"], list)
        assert len(data["heatmap_data"]) == 16  # 4x4 = 16 pairs
        
        # Check heatmap data structure
        heatmap_item = data["heatmap_data"][0]
        assert "x" in heatmap_item
        assert "y" in heatmap_item
        assert "value" in heatmap_item
        assert heatmap_item["x"] in tickers
        assert heatmap_item["y"] in tickers
        assert isinstance(heatmap_item["value"], (int, float))
        
        # Validate cluster mappings
        assert isinstance(data["cluster_leaf_map"], dict)
        # Should have n-1 clusters for n tickers (hierarchical clustering property)
        assert len(data["cluster_leaf_map"]) >= 1
        
        # Each cluster should map to a list of tickers
        for cluster_id, ticker_list in data["cluster_leaf_map"].items():
            assert isinstance(ticker_list, list)
            for ticker in ticker_list:
                assert ticker in tickers
        
        # Validate metadata
        assert data["data_points"] == 100
    
    @patch('app.routers.hrp.get_correlation_data')
    def test_hrp_analyze_all_linkage_methods_mocked(self, mock_get_correlation, client):
        """Test all linkage methods with mocked data."""
        # Create synthetic correlation matrix
        tickers = ['AAPL', 'MSFT', 'GOOGL']
        corr_matrix = pd.DataFrame([
            [1.00, 0.75, 0.60],
            [0.75, 1.00, 0.65],
            [0.60, 0.65, 1.00]
        ], index=tickers, columns=tickers)
        
        mock_returns = pd.DataFrame(np.random.randn(50, 3), columns=tickers)
        mock_metadata = {
            'actual_tickers': tickers,
            'start_date': '2023-01-01',
            'end_date': '2023-06-30',
            'data_points': 50
        }
        mock_get_correlation.return_value = (mock_returns, corr_matrix, mock_metadata)
        
        # Test each linkage method
        linkage_methods = ['single', 'complete', 'average', 'ward']
        
        for method in linkage_methods:
            payload = {
                "tickers": tickers,
                "start_date": "2023-01-01",
                "end_date": "2023-06-30",
                "linkage_method": method
            }
            
            response = client.post("/hrp/analyze", json=payload)
            
            assert response.status_code == 200, f"Failed for method: {method}"
            data = response.json()
            
            # Verify the method was used
            assert data["linkage_method"] == method
            
            # Verify we got all required data
            assert len(data["ordered_tickers"]) == 3
            assert len(data["heatmap_data"]) == 9  # 3x3 = 9
            assert isinstance(data["dendrogram_data"], dict)
            assert isinstance(data["cluster_leaf_map"], dict)
    
    @patch('app.routers.hrp.get_correlation_data')
    def test_hrp_analyze_large_portfolio_mocked(self, mock_get_correlation, client):
        """Test HRP analysis with a larger portfolio (10 tickers)."""
        # Create 10-ticker synthetic correlation matrix
        n_tickers = 10
        tickers = [f"TICK{i}" for i in range(n_tickers)]
        
        # Create a realistic correlation matrix (positive semi-definite)
        random_matrix = np.random.randn(n_tickers, n_tickers)
        corr_matrix = np.corrcoef(random_matrix)
        corr_df = pd.DataFrame(corr_matrix, index=tickers, columns=tickers)
        
        mock_returns = pd.DataFrame(
            np.random.randn(200, n_tickers),
            columns=tickers
        )
        mock_metadata = {
            'actual_tickers': tickers,
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'data_points': 200
        }
        mock_get_correlation.return_value = (mock_returns, corr_df, mock_metadata)
        
        payload = {
            "tickers": tickers,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "linkage_method": "ward"
        }
        
        response = client.post("/hrp/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Validate response for larger portfolio
        assert len(data["ordered_tickers"]) == n_tickers
        assert len(data["heatmap_data"]) == n_tickers * n_tickers
        
        # Should have hierarchical structure with n-1 internal nodes
        assert len(data["cluster_leaf_map"]) >= 1
        
        # Verify all tickers are accounted for in clusters
        all_tickers_in_clusters = set()
        for ticker_list in data["cluster_leaf_map"].values():
            all_tickers_in_clusters.update(ticker_list)
        
        assert all_tickers_in_clusters == set(tickers)
    
    @patch('app.routers.hrp.get_correlation_data')
    def test_hrp_analyze_distinct_clusters_mocked(self, mock_get_correlation, client):
        """Test HRP with distinct cluster structure (block diagonal correlation)."""
        # Create correlation matrix with clear clusters
        tickers = ['TECH1', 'TECH2', 'TECH3', 'BANK1', 'BANK2', 'BANK3']
        
        # Tech stocks highly correlated, banks highly correlated, low cross-correlation
        corr_matrix = pd.DataFrame([
            # TECH1  TECH2  TECH3  BANK1  BANK2  BANK3
            [1.00,  0.90,  0.85,  0.20,  0.15,  0.18],  # TECH1
            [0.90,  1.00,  0.88,  0.18,  0.12,  0.15],  # TECH2
            [0.85,  0.88,  1.00,  0.22,  0.17,  0.20],  # TECH3
            [0.20,  0.18,  0.22,  1.00,  0.92,  0.87],  # BANK1
            [0.15,  0.12,  0.17,  0.92,  1.00,  0.90],  # BANK2
            [0.18,  0.15,  0.20,  0.87,  0.90,  1.00],  # BANK3
        ], index=tickers, columns=tickers)
        
        mock_returns = pd.DataFrame(np.random.randn(100, 6), columns=tickers)
        mock_metadata = {
            'actual_tickers': tickers,
            'start_date': '2023-01-01',
            'end_date': '2023-12-31',
            'data_points': 100
        }
        mock_get_correlation.return_value = (mock_returns, corr_matrix, mock_metadata)
        
        payload = {
            "tickers": tickers,
            "start_date": "2023-01-01",
            "end_date": "2023-12-31",
            "linkage_method": "ward"
        }
        
        response = client.post("/hrp/analyze", json=payload)
        
        assert response.status_code == 200
        data = response.json()
        
        # Should successfully cluster
        assert len(data["ordered_tickers"]) == 6
        assert isinstance(data["dendrogram_data"], dict)
        assert isinstance(data["cluster_leaf_map"], dict)
        
        # Heatmap should be seriated (reordered to show block diagonal structure)
        # After seriation, similar assets should be adjacent
        assert len(data["heatmap_data"]) == 36  # 6x6
        
        # Verify dendrogram has hierarchical structure
        tree = data["dendrogram_data"]
        assert "name" in tree
