"""
API router for Hierarchical Risk Parity (HRP) analysis endpoints.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List
import logging

from app.models.hrp import (
    CorrelationRequest,
    CorrelationResponse,
    HRPRequest,
    HRPResponse
)
from app.services.data_ingestion import (
    get_correlation_data,
    DataIngestionError,
    InsufficientDataError
)
from app.services.hrp_clustering import (
    perform_hrp_clustering,
    correlation_matrix_to_heatmap_data,
    HRPClusteringError
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/correlation",
    response_model=CorrelationResponse,
    status_code=status.HTTP_200_OK,
    summary="Calculate Correlation Matrix",
    description="Fetch historical price data and calculate the Pearson correlation matrix for given tickers"
)
async def calculate_correlation(request: CorrelationRequest) -> CorrelationResponse:
    """
    Calculate correlation matrix for the given tickers and date range.
    
    This endpoint:
    1. Fetches adjusted closing prices from yfinance
    2. Calculates daily percentage returns
    3. Computes the Pearson correlation matrix
    
    The correlation matrix measures the linear relationship between asset returns,
    with values ranging from -1 (perfect negative correlation) to +1 (perfect positive correlation).
    
    Args:
        request: CorrelationRequest containing tickers and date range
        
    Returns:
        CorrelationResponse with correlation matrix and metadata
        
    Raises:
        HTTPException 400: If insufficient data is available
        HTTPException 500: If data fetching fails
    """
    logger.info(
        f"Correlation request received: {len(request.tickers)} tickers, "
        f"{request.start_date} to {request.end_date}"
    )
    
    try:
        # Fetch data and calculate correlation
        returns, correlation_matrix, metadata = get_correlation_data(
            tickers=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        # Convert correlation matrix to list of lists
        corr_matrix_list = correlation_matrix.values.tolist()
        
        # Prepare response
        response = CorrelationResponse(
            tickers=metadata['actual_tickers'],
            correlation_matrix=corr_matrix_list,
            start_date=metadata['start_date'],
            end_date=metadata['end_date'],
            data_points=metadata['data_points']
        )
        
        logger.info(
            f"Successfully calculated correlation matrix for {len(metadata['actual_tickers'])} tickers"
        )
        
        return response
        
    except InsufficientDataError as e:
        logger.warning(f"Insufficient data error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except DataIngestionError as e:
        logger.error(f"Data ingestion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market data: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during correlation calculation"
        )


@router.post(
    "/analyze",
    response_model=HRPResponse,
    status_code=status.HTTP_200_OK,
    summary="Perform Full HRP Analysis",
    description="Complete HRP analysis including correlation matrix, clustering, dendrogram, and heatmap data"
)
async def analyze_hrp(request: HRPRequest) -> HRPResponse:
    """
    Perform complete Hierarchical Risk Parity analysis.
    
    This endpoint:
    1. Fetches historical price data and calculates correlation matrix
    2. Performs hierarchical clustering using the specified method
    3. Generates dendrogram tree structure for visualization
    4. Creates heatmap data with seriated (reordered) correlations
    5. Provides cluster-ticker mappings
    
    The HRP algorithm reorders assets to reveal natural groupings based on
    their correlation structure, which is useful for portfolio construction
    and risk management.
    
    Args:
        request: HRPRequest containing tickers, date range, and clustering parameters
        
    Returns:
        HRPResponse with complete analysis results including:
        - Correlation matrix
        - Dendrogram tree structure
        - Heatmap data (seriated correlations)
        - Cluster mappings
        - Metadata
        
    Raises:
        HTTPException 400: If insufficient data or invalid parameters
        HTTPException 500: If analysis fails
    """
    logger.info(
        f"HRP analysis request: {len(request.tickers)} tickers, "
        f"method={request.linkage_method}, {request.start_date} to {request.end_date}"
    )
    
    try:
        # Step 1: Fetch data and calculate correlation matrix
        logger.info("Step 1: Fetching data and calculating correlation matrix")
        returns, correlation_matrix, metadata = get_correlation_data(
            tickers=request.tickers,
            start_date=request.start_date,
            end_date=request.end_date
        )
        
        logger.info(
            f"Correlation matrix calculated: {len(metadata['actual_tickers'])} tickers, "
            f"{metadata['data_points']} data points"
        )
        
        # Step 2: Perform hierarchical clustering
        logger.info(f"Step 2: Performing HRP clustering with '{request.linkage_method}' method")
        clustering_result = perform_hrp_clustering(
            correlation_matrix=correlation_matrix,
            linkage_method=request.linkage_method
        )
        
        logger.info(
            f"Clustering complete: {len(clustering_result['cluster_map'])} clusters identified"
        )
        
        # Step 3: Generate heatmap data from seriated correlation matrix
        heatmap_data = correlation_matrix_to_heatmap_data(
            clustering_result['seriated_correlation']
        )
        
        # Step 4: Prepare response
        response = HRPResponse(
            ordered_tickers=clustering_result['ordered_tickers'],
            dendrogram_data=clustering_result['dendrogram_tree'],
            heatmap_data=heatmap_data,
            cluster_leaf_map=clustering_result['cluster_map'],
            linkage_method=request.linkage_method,
            data_points=metadata['data_points']
        )
        
        logger.info(
            f"HRP analysis complete for {len(metadata['actual_tickers'])} tickers "
            f"using '{request.linkage_method}' linkage"
        )
        
        return response
        
    except InsufficientDataError as e:
        logger.warning(f"Insufficient data error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    
    except HRPClusteringError as e:
        logger.error(f"HRP clustering error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Clustering failed: {str(e)}"
        )
    
    except DataIngestionError as e:
        logger.error(f"Data ingestion error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch market data: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Unexpected error during HRP analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error occurred during HRP analysis"
        )
