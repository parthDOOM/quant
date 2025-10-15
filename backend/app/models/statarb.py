"""
Statistical Arbitrage Models

Pydantic models for the Statistical Arbitrage API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class PairTestRequest(BaseModel):
    """Request model for testing cointegration between two assets"""
    ticker_a: str = Field(..., description="First asset ticker symbol")
    ticker_b: str = Field(..., description="Second asset ticker symbol")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")


class CointResult(BaseModel):
    """Result of cointegration test between two assets"""
    ticker_a: str
    ticker_b: str
    p_value: float = Field(..., description="Engle-Granger test p-value")
    test_statistic: float = Field(..., description="Test statistic value")
    is_cointegrated: bool = Field(..., description="Whether pair is cointegrated (p < 0.05)")
    hedge_ratio: float = Field(..., description="Optimal hedge ratio from OLS regression")
    half_life: float = Field(..., description="Mean reversion half-life in days")
    spread_mean: float = Field(..., description="Mean of the spread")
    spread_std: float = Field(..., description="Standard deviation of the spread")
    correlation: float = Field(..., description="Pearson correlation between the two series")


class FindPairsRequest(BaseModel):
    """Request model for finding cointegrated pairs in a cluster"""
    tickers: List[str] = Field(..., min_length=2, description="List of ticker symbols to test")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    p_value_threshold: float = Field(
        default=0.05,
        ge=0.0,
        le=1.0,
        description="P-value threshold for cointegration significance"
    )


class CointegratedPair(BaseModel):
    """A cointegrated asset pair with statistical metrics"""
    asset_1: str
    asset_2: str
    p_value: float
    test_statistic: float
    hedge_ratio: float
    half_life: float
    correlation: float


class FindPairsResponse(BaseModel):
    """Response model for pair finder endpoint"""
    pairs: List[CointegratedPair] = Field(..., description="List of cointegrated pairs found")
    total_combinations_tested: int = Field(..., description="Total number of pairs tested")
    cointegrated_count: int = Field(..., description="Number of cointegrated pairs found")


class SpreadAnalysisRequest(BaseModel):
    """Request model for spread analysis"""
    ticker_a: str = Field(..., description="First asset ticker symbol")
    ticker_b: str = Field(..., description="Second asset ticker symbol")
    start_date: str = Field(..., description="Start date in YYYY-MM-DD format")
    end_date: str = Field(..., description="End date in YYYY-MM-DD format")
    window: int = Field(
        default=20,
        ge=5,
        le=252,
        description="Rolling window size for z-score calculation"
    )
    entry_threshold: float = Field(
        default=2.0,
        ge=0.0,
        description="Z-score threshold for entry signals"
    )
    exit_threshold: float = Field(
        default=0.0,
        description="Z-score threshold for exit signals"
    )


class SpreadPoint(BaseModel):
    """A single point in the spread time series"""
    date: str = Field(..., description="Date in YYYY-MM-DD format")
    spread: float = Field(..., description="Spread value")
    zscore: float = Field(..., description="Z-score of the spread")
    signal: Optional[str] = Field(
        None,
        description="Trading signal: 'long', 'short', 'exit', or None"
    )


class SpreadStatistics(BaseModel):
    """Statistical metrics for the spread"""
    mean: float
    std: float
    min: float
    max: float
    sharpe: Optional[float] = None


class SpreadAnalysisResponse(BaseModel):
    """Response model for spread analysis endpoint"""
    ticker_a: str
    ticker_b: str
    hedge_ratio: float
    half_life: float
    spread_data: List[SpreadPoint] = Field(..., description="Time series of spread values")
    statistics: SpreadStatistics = Field(..., description="Statistical metrics")
