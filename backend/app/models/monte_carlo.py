"""Pydantic models for Monte Carlo simulation."""
from pydantic import BaseModel, Field
from typing import List, Dict


class MonteCarloRequest(BaseModel):
    """Request model for Monte Carlo simulation."""
    tickers: List[str] = Field(..., description="List of ticker symbols", min_length=1)
    initial_prices: List[float] = Field(..., description="Starting prices for each asset")
    expected_returns: List[float] = Field(..., description="Daily expected returns (e.g., 0.001 = 0.1%)")
    covariance_matrix: List[List[float]] = Field(..., description="Covariance matrix (n x n)")
    num_simulations: int = Field(1000, description="Number of simulation paths", ge=100, le=10000)
    num_days: int = Field(252, description="Number of days to simulate", ge=1, le=1000)
    
    class Config:
        json_schema_extra = {
            "example": {
                "tickers": ["AAPL", "MSFT"],
                "initial_prices": [150.0, 300.0],
                "expected_returns": [0.0008, 0.001],
                "covariance_matrix": [
                    [0.0004, 0.0001],
                    [0.0001, 0.0003]
                ],
                "num_simulations": 1000,
                "num_days": 252
            }
        }


class AssetStatistics(BaseModel):
    """Statistics for a single asset."""
    mean: float
    std: float
    percentile_5: float
    percentile_50: float
    percentile_95: float


class PortfolioStatistics(BaseModel):
    """Portfolio statistics."""
    mean: float
    std: float
    percentile_5: float
    percentile_25: float
    percentile_50: float
    percentile_75: float
    percentile_95: float
    min: float
    max: float


class MonteCarloResponse(BaseModel):
    """Response model for Monte Carlo simulation."""
    tickers: List[str]
    num_simulations: int
    num_days: int
    portfolio_statistics: PortfolioStatistics
    asset_statistics: Dict[str, AssetStatistics]
    sample_paths: List[List[float]]
    final_value_distribution: List[float]
    execution_time_ms: float = Field(default=0.0, description="Execution time in milliseconds")
