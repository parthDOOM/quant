"""
Pydantic models for Hierarchical Risk Parity (HRP) analysis.
"""
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict
from datetime import date


class CorrelationRequest(BaseModel):
    """Request model for correlation matrix calculation."""
    
    tickers: List[str] = Field(
        ...,
        min_length=2,
        max_length=50,  # Security: Limit to prevent resource exhaustion
        description="List of asset tickers (minimum 2, maximum 50)"
    )
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format",
        pattern=r'^\d{4}-\d{2}-\d{2}$'  # Security: Enforce date format pattern
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format",
        pattern=r'^\d{4}-\d{2}-\d{2}$'  # Security: Enforce date format pattern
    )
    
    @field_validator('tickers')
    @classmethod
    def validate_tickers(cls, v: List[str]) -> List[str]:
        """Validate and sanitize ticker symbols with security checks."""
        if not v:
            raise ValueError("Tickers list cannot be empty")
        
        # Security: Validate each ticker
        cleaned_tickers = []
        for ticker in v:
            ticker_stripped = ticker.strip()
            
            # Security: Check length
            if len(ticker_stripped) == 0:
                raise ValueError("Empty ticker symbol not allowed")
            if len(ticker_stripped) > 10:
                raise ValueError(f"Ticker symbol too long (max 10 chars): {ticker}")
            
            # Security: Allow only alphanumeric, dots, hyphens (valid ticker chars)
            if not all(c.isalnum() or c in '.-' for c in ticker_stripped):
                raise ValueError(f"Invalid characters in ticker symbol: {ticker}")
            
            cleaned_tickers.append(ticker_stripped.upper())
        
        # Remove duplicates while preserving order
        seen = set()
        unique_tickers = []
        for ticker in cleaned_tickers:
            if ticker not in seen:
                seen.add(ticker)
                unique_tickers.append(ticker)
        
        if len(unique_tickers) < 2:
            raise ValueError("At least 2 unique tickers are required")
        
        return unique_tickers
    
    @field_validator('start_date', 'end_date')
    @classmethod
    def validate_date_format(cls, v: str) -> str:
        """Validate date format."""
        try:
            # Try parsing the date to validate format
            date.fromisoformat(v)
            return v
        except ValueError:
            raise ValueError(f"Invalid date format: {v}. Expected YYYY-MM-DD")
    
    class Config:
        json_schema_extra = {
            "example": {
                "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
                "start_date": "2023-01-01",
                "end_date": "2023-12-31"
            }
        }


class CorrelationResponse(BaseModel):
    """Response model for correlation matrix calculation."""
    
    tickers: List[str] = Field(
        ...,
        description="List of tickers in the order they appear in the correlation matrix"
    )
    correlation_matrix: List[List[float]] = Field(
        ...,
        description="Correlation matrix as a 2D list"
    )
    start_date: str = Field(
        ...,
        description="Actual start date of data used"
    )
    end_date: str = Field(
        ...,
        description="Actual end date of data used"
    )
    data_points: int = Field(
        ...,
        description="Number of trading days used in calculation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "tickers": ["AAPL", "MSFT", "GOOGL"],
                "correlation_matrix": [
                    [1.0, 0.75, 0.68],
                    [0.75, 1.0, 0.72],
                    [0.68, 0.72, 1.0]
                ],
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "data_points": 252
            }
        }


class HRPRequest(BaseModel):
    """Request model for full HRP analysis."""
    
    tickers: List[str] = Field(
        ...,
        min_length=3,
        description="List of asset tickers (minimum 3 required for clustering)"
    )
    start_date: str = Field(
        ...,
        description="Start date in YYYY-MM-DD format"
    )
    end_date: str = Field(
        ...,
        description="End date in YYYY-MM-DD format"
    )
    linkage_method: Optional[str] = Field(
        default='ward',
        description="Hierarchical clustering linkage method"
    )
    
    @field_validator('tickers')
    @classmethod
    def validate_tickers(cls, v: List[str]) -> List[str]:
        """Validate and clean ticker symbols."""
        if not v:
            raise ValueError("Tickers list cannot be empty")
        
        # Remove duplicates and convert to uppercase
        cleaned = list(set(ticker.strip().upper() for ticker in v))
        
        if len(cleaned) < 3:
            raise ValueError("At least 3 unique tickers are required for HRP analysis")
        
        return cleaned
    
    @field_validator('linkage_method')
    @classmethod
    def validate_linkage_method(cls, v: str) -> str:
        """Validate linkage method."""
        valid_methods = ['single', 'complete', 'average', 'ward']
        if v not in valid_methods:
            raise ValueError(
                f"Invalid linkage method: {v}. "
                f"Must be one of: {', '.join(valid_methods)}"
            )
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "tickers": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
                "start_date": "2023-01-01",
                "end_date": "2023-12-31",
                "linkage_method": "ward"
            }
        }


class DendrogramNode(BaseModel):
    """Model for a node in the dendrogram tree structure."""
    
    name: str = Field(..., description="Node name (ticker for leaves, cluster ID for internal nodes)")
    height: Optional[float] = Field(None, description="Height of the node in the dendrogram")
    children: Optional[List['DendrogramNode']] = Field(None, description="Child nodes")
    
    class Config:
        json_schema_extra = {
            "example": {
                "name": "cluster_1",
                "height": 0.5,
                "children": [
                    {"name": "AAPL", "height": 0.0, "children": None},
                    {"name": "MSFT", "height": 0.0, "children": None}
                ]
            }
        }


class HeatmapCell(BaseModel):
    """Model for a single cell in the correlation heatmap."""
    
    x: str = Field(..., description="X-axis ticker")
    y: str = Field(..., description="Y-axis ticker")
    value: float = Field(..., description="Correlation value")
    
    class Config:
        json_schema_extra = {
            "example": {
                "x": "AAPL",
                "y": "MSFT",
                "value": 0.75
            }
        }


class HRPResponse(BaseModel):
    """Response model for full HRP analysis."""
    
    ordered_tickers: List[str] = Field(
        ...,
        description="Tickers ordered according to hierarchical clustering"
    )
    dendrogram_data: DendrogramNode = Field(
        ...,
        description="Hierarchical tree structure for dendrogram visualization"
    )
    heatmap_data: List[HeatmapCell] = Field(
        ...,
        description="Correlation heatmap data in long format"
    )
    cluster_leaf_map: Dict[int, List[str]] = Field(
        ...,
        description="Mapping of cluster IDs to their constituent tickers"
    )
    linkage_method: str = Field(
        ...,
        description="Linkage method used for clustering"
    )
    data_points: int = Field(
        ...,
        description="Number of trading days used in calculation"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "ordered_tickers": ["AAPL", "MSFT", "GOOGL", "AMZN"],
                "dendrogram_data": {
                    "name": "root",
                    "height": 1.0,
                    "children": []
                },
                "heatmap_data": [
                    {"x": "AAPL", "y": "MSFT", "value": 0.75}
                ],
                "cluster_leaf_map": {
                    0: ["AAPL", "MSFT"],
                    1: ["GOOGL", "AMZN"]
                },
                "linkage_method": "ward",
                "data_points": 252
            }
        }
