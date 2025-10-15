"""
Unit tests for HRP clustering service.
"""
import pytest
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage

from app.services.hrp_clustering import (
    correlation_to_distance,
    perform_hierarchical_clustering,
    get_seriation_order,
    seriate_matrix,
    linkage_to_tree_dict,
    get_cluster_leaves,
    perform_hrp_clustering,
    correlation_matrix_to_heatmap_data,
    HRPClusteringError
)


@pytest.mark.unit
class TestCorrelationToDistance:
    """Tests for correlation to distance transformation."""
    
    def test_perfect_correlation_to_distance(self):
        """Test that perfect correlation (1.0) maps to distance 0.0."""
        corr = pd.DataFrame([[1.0, 1.0], [1.0, 1.0]], columns=['A', 'B'])
        distance = correlation_to_distance(corr)
        
        # sqrt(0.5 * (1 - 1)) = 0
        assert np.isclose(distance[0, 1], 0.0)
    
    def test_negative_correlation_to_distance(self):
        """Test that perfect negative correlation (-1.0) maps to maximum distance."""
        corr = pd.DataFrame([[1.0, -1.0], [-1.0, 1.0]], columns=['A', 'B'])
        distance = correlation_to_distance(corr)
        
        # sqrt(0.5 * (1 - (-1))) = sqrt(1) = 1.0
        assert np.isclose(distance[0, 1], 1.0)
    
    def test_zero_correlation_to_distance(self):
        """Test that zero correlation maps to intermediate distance."""
        corr = pd.DataFrame([[1.0, 0.0], [0.0, 1.0]], columns=['A', 'B'])
        distance = correlation_to_distance(corr)
        
        # sqrt(0.5 * (1 - 0)) = sqrt(0.5) ≈ 0.707
        assert np.isclose(distance[0, 1], np.sqrt(0.5))
    
    def test_diagonal_is_zero(self):
        """Test that diagonal of distance matrix is zero."""
        corr = pd.DataFrame([
            [1.0, 0.5, 0.3],
            [0.5, 1.0, 0.6],
            [0.3, 0.6, 1.0]
        ], columns=['A', 'B', 'C'])
        
        distance = correlation_to_distance(corr)
        
        assert np.allclose(np.diag(distance), 0.0)
    
    def test_invalid_input(self):
        """Test error handling for invalid input."""
        # Non-square matrix
        corr = pd.DataFrame([[1.0, 0.5], [0.5, 1.0], [0.3, 0.7]], columns=['A', 'B'])
        
        with pytest.raises(HRPClusteringError):
            correlation_to_distance(corr)


@pytest.mark.unit
class TestHierarchicalClustering:
    """Tests for hierarchical clustering."""
    
    def test_clustering_simple_matrix(self):
        """Test clustering with a simple 3x3 distance matrix."""
        # Create simple distance matrix where A and B are close, C is far
        distance = np.array([
            [0.0, 0.1, 0.9],
            [0.1, 0.0, 0.8],
            [0.9, 0.8, 0.0]
        ])
        
        Z = perform_hierarchical_clustering(distance, 'ward')
        
        # Linkage matrix should have shape (n-1, 4) for n assets
        assert Z.shape == (2, 4)
        
        # First merge should be A and B (indices 0 and 1)
        assert {int(Z[0, 0]), int(Z[0, 1])} == {0, 1}
    
    def test_different_linkage_methods(self):
        """Test that different linkage methods work."""
        distance = np.array([
            [0.0, 0.2, 0.8],
            [0.2, 0.0, 0.7],
            [0.8, 0.7, 0.0]
        ])
        
        for method in ['single', 'complete', 'average', 'ward']:
            Z = perform_hierarchical_clustering(distance, method)
            assert Z.shape == (2, 4)
    
    def test_invalid_linkage_method(self):
        """Test error handling for invalid linkage method."""
        distance = np.array([[0.0, 0.5], [0.5, 0.0]])
        
        with pytest.raises(HRPClusteringError):
            perform_hierarchical_clustering(distance, 'invalid_method')


@pytest.mark.unit
class TestSeriation:
    """Tests for matrix seriation."""
    
    def test_get_seriation_order(self):
        """Test extraction of seriation order from linkage matrix."""
        # Simple 3-asset linkage matrix
        distance = np.array([
            [0.0, 0.1, 0.9],
            [0.1, 0.0, 0.8],
            [0.9, 0.8, 0.0]
        ])
        Z = perform_hierarchical_clustering(distance, 'ward')
        
        order = get_seriation_order(Z)
        
        # Should return 3 indices
        assert len(order) == 3
        
        # Should be a permutation of [0, 1, 2]
        assert set(order) == {0, 1, 2}
    
    def test_seriate_matrix(self):
        """Test matrix seriation."""
        # Create a matrix with explicit index
        matrix = pd.DataFrame([
            [1.0, 0.8, 0.2],
            [0.8, 1.0, 0.3],
            [0.2, 0.3, 1.0]
        ], columns=['A', 'B', 'C'], index=['A', 'B', 'C'])
        
        # Reorder: [2, 0, 1] -> ['C', 'A', 'B']
        order = [2, 0, 1]
        seriated = seriate_matrix(matrix, order)
        
        # Check new order
        assert list(seriated.columns) == ['C', 'A', 'B']
        assert list(seriated.index) == ['C', 'A', 'B']
        
        # Check values are correctly reordered
        assert seriated.iloc[0, 0] == 1.0  # C-C correlation
        assert np.isclose(seriated.iloc[0, 1], 0.2)  # C-A correlation


@pytest.mark.unit
class TestTreeConversion:
    """Tests for linkage matrix to tree conversion."""
    
    def test_linkage_to_tree_dict(self):
        """Test conversion of linkage matrix to tree dictionary."""
        # Simple 3-asset case
        distance = np.array([
            [0.0, 0.1, 0.9],
            [0.1, 0.0, 0.8],
            [0.9, 0.8, 0.0]
        ])
        Z = perform_hierarchical_clustering(distance, 'ward')
        labels = ['AAPL', 'MSFT', 'GOOGL']
        
        tree = linkage_to_tree_dict(Z, labels)
        
        # Root should have children
        assert 'children' in tree
        assert tree['children'] is not None
        assert len(tree['children']) == 2
        
        # Should have height
        assert 'height' in tree
        assert tree['height'] > 0
    
    def test_tree_has_correct_leaf_names(self):
        """Test that leaf nodes have correct ticker names."""
        distance = np.array([[0.0, 0.5], [0.5, 0.0]])
        Z = perform_hierarchical_clustering(distance, 'ward')
        labels = ['AAPL', 'MSFT']
        
        tree = linkage_to_tree_dict(Z, labels)
        
        # Extract all leaf names
        def get_leaf_names(node):
            if node['children'] is None:
                return [node['name']]
            else:
                left_leaves = get_leaf_names(node['children'][0])
                right_leaves = get_leaf_names(node['children'][1])
                return left_leaves + right_leaves
        
        leaf_names = get_leaf_names(tree)
        assert set(leaf_names) == {'AAPL', 'MSFT'}


@pytest.mark.unit
class TestClusterMapping:
    """Tests for cluster-to-ticker mapping."""
    
    def test_get_cluster_leaves(self):
        """Test extraction of cluster-ticker mappings."""
        # Simple 3-asset case
        distance = np.array([
            [0.0, 0.1, 0.9],
            [0.1, 0.0, 0.8],
            [0.9, 0.8, 0.0]
        ])
        Z = perform_hierarchical_clustering(distance, 'ward')
        labels = ['AAPL', 'MSFT', 'GOOGL']
        
        cluster_map = get_cluster_leaves(Z, labels)
        
        # Should have mappings
        assert len(cluster_map) > 0
        
        # All tickers should appear in mappings
        all_tickers = []
        for tickers in cluster_map.values():
            all_tickers.extend(tickers)
        
        assert set(all_tickers) == set(labels)


@pytest.mark.unit
class TestCompleteHRPPipeline:
    """Tests for the complete HRP clustering pipeline."""
    
    def test_perform_hrp_clustering(self):
        """Test complete HRP clustering pipeline."""
        # Create correlation matrix
        corr = pd.DataFrame([
            [1.0, 0.8, 0.2, 0.3],
            [0.8, 1.0, 0.3, 0.2],
            [0.2, 0.3, 1.0, 0.7],
            [0.3, 0.2, 0.7, 1.0]
        ], columns=['AAPL', 'MSFT', 'GOOGL', 'AMZN'])
        
        result = perform_hrp_clustering(corr, 'ward')
        
        # Check all expected keys are present
        assert 'linkage_matrix' in result
        assert 'ordered_tickers' in result
        assert 'seriated_correlation' in result
        assert 'dendrogram_tree' in result
        assert 'cluster_map' in result
        
        # Check ordered_tickers
        assert len(result['ordered_tickers']) == 4
        assert set(result['ordered_tickers']) == {'AAPL', 'MSFT', 'GOOGL', 'AMZN'}
        
        # Check seriated correlation
        assert result['seriated_correlation'].shape == (4, 4)
        
        # Check linkage matrix
        assert result['linkage_matrix'].shape == (3, 4)  # n-1 rows for n assets
    
    def test_different_linkage_methods_in_pipeline(self):
        """Test that pipeline works with different linkage methods."""
        corr = pd.DataFrame([
            [1.0, 0.6, 0.3],
            [0.6, 1.0, 0.4],
            [0.3, 0.4, 1.0]
        ], columns=['A', 'B', 'C'])
        
        for method in ['single', 'complete', 'average', 'ward']:
            result = perform_hrp_clustering(corr, method)
            assert len(result['ordered_tickers']) == 3


@pytest.mark.unit
class TestHeatmapDataConversion:
    """Tests for heatmap data conversion."""
    
    def test_correlation_matrix_to_heatmap_data(self):
        """Test conversion of correlation matrix to heatmap format."""
        corr = pd.DataFrame([
            [1.0, 0.5, 0.3],
            [0.5, 1.0, 0.6],
            [0.3, 0.6, 1.0]
        ], columns=['AAPL', 'MSFT', 'GOOGL'])
        
        heatmap_data = correlation_matrix_to_heatmap_data(corr)
        
        # Should have n*n cells
        assert len(heatmap_data) == 9
        
        # Each cell should have x, y, value
        for cell in heatmap_data:
            assert 'x' in cell
            assert 'y' in cell
            assert 'value' in cell
        
        # Check a specific cell
        aapl_msft_cell = [c for c in heatmap_data if c['x'] == 'AAPL' and c['y'] == 'MSFT'][0]
        assert np.isclose(aapl_msft_cell['value'], 0.5)
    
    def test_heatmap_includes_all_pairs(self):
        """Test that heatmap includes all ticker pairs."""
        corr = pd.DataFrame([
            [1.0, 0.7],
            [0.7, 1.0]
        ], columns=['A', 'B'])
        
        heatmap_data = correlation_matrix_to_heatmap_data(corr)
        
        pairs = {(cell['x'], cell['y']) for cell in heatmap_data}
        
        assert ('A', 'A') in pairs
        assert ('A', 'B') in pairs
        assert ('B', 'A') in pairs
        assert ('B', 'B') in pairs
