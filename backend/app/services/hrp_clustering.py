"""
Hierarchical Risk Parity (HRP) clustering service.
Implements hierarchical clustering on correlation matrices and matrix seriation.
"""
import pandas as pd
import numpy as np
from scipy.cluster.hierarchy import linkage, dendrogram, leaves_list, to_tree
from scipy.spatial.distance import squareform
from typing import Dict, List, Tuple, Any
import logging

logger = logging.getLogger(__name__)


class HRPClusteringError(Exception):
    """Custom exception for HRP clustering errors."""
    pass


def correlation_to_distance(correlation_matrix: pd.DataFrame) -> np.ndarray:
    """
    Convert correlation matrix to distance matrix.
    
    The formula used is: distance = sqrt(0.5 * (1 - correlation))
    This maps correlations in [-1, 1] to distances in [0, sqrt(2)].
    
    Args:
        correlation_matrix: Square correlation matrix
        
    Returns:
        Distance matrix as numpy array
        
    Raises:
        HRPClusteringError: If correlation matrix is invalid
    """
    # Validate input
    if not isinstance(correlation_matrix, pd.DataFrame):
        raise HRPClusteringError("Correlation matrix must be a pandas DataFrame")
    
    if correlation_matrix.shape[0] != correlation_matrix.shape[1]:
        raise HRPClusteringError("Correlation matrix must be square")
    
    # Convert to numpy array for calculation
    corr_array = correlation_matrix.values
    
    # Calculate distance: sqrt(0.5 * (1 - correlation))
    distance_matrix = np.sqrt(0.5 * (1 - corr_array))
    
    # Ensure diagonal is zero (distance from asset to itself)
    np.fill_diagonal(distance_matrix, 0)
    
    logger.debug(f"Converted {correlation_matrix.shape[0]}x{correlation_matrix.shape[1]} "
                 f"correlation matrix to distance matrix")
    
    return distance_matrix


def perform_hierarchical_clustering(
    distance_matrix: np.ndarray,
    linkage_method: str = 'ward'
) -> np.ndarray:
    """
    Perform hierarchical agglomerative clustering on distance matrix.
    
    Args:
        distance_matrix: Square distance matrix
        linkage_method: Clustering method ('single', 'complete', 'average', 'ward')
        
    Returns:
        Linkage matrix (Z) encoding the hierarchical clustering
        
    Raises:
        HRPClusteringError: If clustering fails
    """
    valid_methods = ['single', 'complete', 'average', 'ward']
    if linkage_method not in valid_methods:
        raise HRPClusteringError(
            f"Invalid linkage method: {linkage_method}. "
            f"Must be one of: {', '.join(valid_methods)}"
        )
    
    try:
        # Convert square distance matrix to condensed form required by scipy
        condensed_distance = squareform(distance_matrix, checks=False)
        
        # Perform hierarchical clustering
        linkage_matrix = linkage(condensed_distance, method=linkage_method)
        
        logger.info(f"Hierarchical clustering complete using '{linkage_method}' linkage")
        logger.debug(f"Linkage matrix shape: {linkage_matrix.shape}")
        
        return linkage_matrix
        
    except Exception as e:
        logger.error(f"Clustering failed: {str(e)}")
        raise HRPClusteringError(f"Failed to perform hierarchical clustering: {str(e)}")


def get_seriation_order(linkage_matrix: np.ndarray) -> List[int]:
    """
    Extract the optimal leaf ordering from the linkage matrix.
    This ordering reveals the block-diagonal structure of the correlation matrix.
    
    Args:
        linkage_matrix: Linkage matrix from hierarchical clustering
        
    Returns:
        List of indices representing the optimal ordering
        
    Raises:
        HRPClusteringError: If extraction fails
    """
    try:
        # Extract optimal leaf order
        order = leaves_list(linkage_matrix)
        
        logger.debug(f"Extracted seriation order: {order}")
        
        return order.tolist()
        
    except Exception as e:
        logger.error(f"Failed to extract seriation order: {str(e)}")
        raise HRPClusteringError(f"Failed to extract leaf ordering: {str(e)}")


def seriate_matrix(
    matrix: pd.DataFrame,
    order: List[int]
) -> pd.DataFrame:
    """
    Reorder (seriate) a matrix according to the given ordering.
    
    Args:
        matrix: Square matrix to reorder
        order: List of indices representing the new order
        
    Returns:
        Reordered matrix
        
    Raises:
        HRPClusteringError: If seriation fails
    """
    try:
        # Reorder both rows and columns using integer positions
        seriated_matrix = matrix.iloc[order, order]
        
        # Preserve the original column and index labels in the new order
        seriated_matrix.columns = [matrix.columns[i] for i in order]
        seriated_matrix.index = [matrix.index[i] for i in order]
        
        logger.debug(f"Matrix seriated with order: {order}")
        
        return seriated_matrix
        
    except Exception as e:
        logger.error(f"Matrix seriation failed: {str(e)}")
        raise HRPClusteringError(f"Failed to seriate matrix: {str(e)}")


def linkage_to_tree_dict(linkage_matrix: np.ndarray, labels: List[str]) -> Dict[str, Any]:
    """
    Convert scipy linkage matrix to nested dictionary structure for dendrogram visualization.
    
    Args:
        linkage_matrix: Linkage matrix from hierarchical clustering
        labels: List of asset labels (tickers)
        
    Returns:
        Nested dictionary representing the tree structure
        
    Raises:
        HRPClusteringError: If conversion fails
    """
    try:
        # Convert linkage matrix to tree object
        tree = to_tree(linkage_matrix)
        
        # Recursively build dictionary structure
        def tree_to_dict(node, labels: List[str]) -> Dict[str, Any]:
            if node.is_leaf():
                # Leaf node - return ticker name
                return {
                    'name': labels[node.id],
                    'height': 0.0,
                    'children': None
                }
            else:
                # Internal node - recursively process children
                return {
                    'name': f'cluster_{node.id}',
                    'height': float(node.dist),
                    'children': [
                        tree_to_dict(node.left, labels),
                        tree_to_dict(node.right, labels)
                    ]
                }
        
        tree_dict = tree_to_dict(tree, labels)
        
        logger.debug("Successfully converted linkage matrix to tree dictionary")
        
        return tree_dict
        
    except Exception as e:
        logger.error(f"Failed to convert linkage to tree: {str(e)}")
        raise HRPClusteringError(f"Failed to build tree structure: {str(e)}")


def get_cluster_leaves(linkage_matrix: np.ndarray, labels: List[str]) -> Dict[int, List[str]]:
    """
    Extract mapping of cluster IDs to their constituent leaf nodes (tickers).
    
    Args:
        linkage_matrix: Linkage matrix from hierarchical clustering
        labels: List of asset labels (tickers)
        
    Returns:
        Dictionary mapping cluster ID to list of tickers
        
    Raises:
        HRPClusteringError: If extraction fails
    """
    try:
        n = len(labels)
        tree = to_tree(linkage_matrix)
        
        cluster_map = {}
        
        def get_leaves(node, cluster_id: int) -> List[str]:
            """Recursively get all leaf nodes under a node."""
            if node.is_leaf():
                return [labels[node.id]]
            else:
                left_leaves = get_leaves(node.left, node.left.id)
                right_leaves = get_leaves(node.right, node.right.id)
                all_leaves = left_leaves + right_leaves
                
                # Only store non-leaf clusters
                if not node.is_leaf():
                    cluster_map[cluster_id] = all_leaves
                
                return all_leaves
        
        # Start from root
        get_leaves(tree, tree.id)
        
        logger.debug(f"Extracted {len(cluster_map)} cluster-leaf mappings")
        
        return cluster_map
        
    except Exception as e:
        logger.error(f"Failed to extract cluster leaves: {str(e)}")
        raise HRPClusteringError(f"Failed to build cluster map: {str(e)}")


def perform_hrp_clustering(
    correlation_matrix: pd.DataFrame,
    linkage_method: str = 'ward'
) -> Dict[str, Any]:
    """
    Complete HRP clustering pipeline: distance conversion, clustering, and seriation.
    
    This is the main function that orchestrates the entire clustering process:
    1. Convert correlation to distance
    2. Perform hierarchical clustering
    3. Extract seriation order
    4. Reorder correlation matrix
    5. Build tree structure for visualization
    6. Extract cluster-ticker mappings
    
    Args:
        correlation_matrix: Correlation matrix (DataFrame with ticker labels)
        linkage_method: Clustering method ('single', 'complete', 'average', 'ward')
        
    Returns:
        Dictionary containing:
            - linkage_matrix: Linkage matrix (numpy array)
            - ordered_tickers: List of tickers in clustered order
            - seriated_correlation: Reordered correlation matrix
            - dendrogram_tree: Tree structure for D3.js visualization
            - cluster_map: Mapping of cluster IDs to tickers
            
    Raises:
        HRPClusteringError: If any step fails
    """
    logger.info(f"Starting HRP clustering with '{linkage_method}' linkage method")
    
    # Get ticker labels
    tickers = list(correlation_matrix.columns)
    n_assets = len(tickers)
    
    logger.info(f"Processing {n_assets} assets: {tickers}")
    
    # Step 1: Convert correlation to distance
    distance_matrix = correlation_to_distance(correlation_matrix)
    
    # Step 2: Perform hierarchical clustering
    linkage_matrix = perform_hierarchical_clustering(distance_matrix, linkage_method)
    
    # Step 3: Get seriation order
    order = get_seriation_order(linkage_matrix)
    
    # Step 4: Reorder tickers and correlation matrix
    ordered_tickers = [tickers[i] for i in order]
    seriated_correlation = seriate_matrix(correlation_matrix, order)
    
    # Step 5: Build tree structure for visualization
    dendrogram_tree = linkage_to_tree_dict(linkage_matrix, tickers)
    
    # Step 6: Get cluster-ticker mappings
    cluster_map = get_cluster_leaves(linkage_matrix, tickers)
    
    logger.info(f"HRP clustering complete. Ordered tickers: {ordered_tickers}")
    
    return {
        'linkage_matrix': linkage_matrix,
        'ordered_tickers': ordered_tickers,
        'seriated_correlation': seriated_correlation,
        'dendrogram_tree': dendrogram_tree,
        'cluster_map': cluster_map
    }


def correlation_matrix_to_heatmap_data(
    correlation_matrix: pd.DataFrame
) -> List[Dict[str, Any]]:
    """
    Convert correlation matrix to long-format data for heatmap visualization.
    
    Args:
        correlation_matrix: Square correlation matrix
        
    Returns:
        List of dictionaries, each containing x, y, and value
    """
    heatmap_data = []
    
    tickers = list(correlation_matrix.columns)
    
    for i, ticker_x in enumerate(tickers):
        for j, ticker_y in enumerate(tickers):
            heatmap_data.append({
                'x': ticker_x,
                'y': ticker_y,
                'value': float(correlation_matrix.iloc[i, j])
            })
    
    logger.debug(f"Generated {len(heatmap_data)} heatmap cells")
    
    return heatmap_data
