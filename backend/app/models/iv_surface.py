"""
Pydantic models for IV Surface API.

These models define the request/response schema for the implied volatility
surface visualization endpoint.
"""

from pydantic import BaseModel, Field, validator
from typing import List, Optional, Literal
from datetime import date


class IVSurfaceRequest(BaseModel):
    """Request parameters for IV surface calculation."""
    
    ticker: str = Field(
        ...,
        description="Stock ticker symbol",
        example="AAPL",
        min_length=1,
        max_length=10
    )
    
    expiration_filter: Optional[Literal['first', 'all', 'near_term']] = Field(
        default='first',
        description=(
            "Filter for expiration dates:\n"
            "- 'first': Only the nearest expiration\n"
            "- 'near_term': Expirations within 90 days\n"
            "- 'all': All available expirations"
        )
    )
    
    min_volume: Optional[int] = Field(
        default=10,
        description="Minimum volume filter for options contracts",
        ge=0
    )
    
    @validator('ticker')
    def ticker_uppercase(cls, v):
        """Convert ticker to uppercase."""
        return v.upper().strip()


class OptionContractIV(BaseModel):
    """Individual option contract with calculated IV."""
    
    strike: float = Field(..., description="Strike price")
    moneyness: float = Field(..., description="Strike / Spot ratio")
    time_to_expiry: float = Field(..., description="Time to expiration in years")
    bid: float = Field(..., description="Bid price")
    ask: float = Field(..., description="Ask price")
    mid_price: float = Field(..., description="Mid price (bid+ask)/2")
    volume: int = Field(..., description="Trading volume")
    open_interest: int = Field(..., description="Open interest")
    implied_volatility: Optional[float] = Field(
        None,
        description="Calculated implied volatility (0-1 scale, e.g., 0.25 = 25%)"
    )
    expiration: str = Field(..., description="Expiration date (YYYY-MM-DD)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "strike": 250.0,
                "moneyness": 0.998,
                "time_to_expiry": 0.00274,
                "bid": 3.0,
                "ask": 3.2,
                "mid_price": 3.1,
                "volume": 1523,
                "open_interest": 5678,
                "implied_volatility": 0.543,
                "expiration": "2025-10-17"
            }
        }


class IVSurfaceMetrics(BaseModel):
    """Summary metrics for the IV surface."""
    
    atm_call_iv: Optional[float] = Field(
        None,
        description="At-the-money call implied volatility"
    )
    atm_put_iv: Optional[float] = Field(
        None,
        description="At-the-money put implied volatility"
    )
    atm_iv_avg: Optional[float] = Field(
        None,
        description="Average ATM IV (mean of call and put)"
    )
    
    put_call_skew: Optional[float] = Field(
        None,
        description="Volatility skew (OTM put IV - OTM call IV)"
    )
    
    iv_range_calls: Optional[dict] = Field(
        None,
        description="IV statistics for calls (min, max, mean, std)"
    )
    iv_range_puts: Optional[dict] = Field(
        None,
        description="IV statistics for puts (min, max, mean, std)"
    )
    
    total_call_contracts: int = Field(
        ...,
        description="Total number of call contracts analyzed"
    )
    total_put_contracts: int = Field(
        ...,
        description="Total number of put contracts analyzed"
    )
    
    successful_call_ivs: int = Field(
        ...,
        description="Number of calls with successfully calculated IV"
    )
    successful_put_ivs: int = Field(
        ...,
        description="Number of puts with successfully calculated IV"
    )
    
    expiration_dates: List[str] = Field(
        ...,
        description="List of expiration dates included in analysis"
    )


class IVSurfaceResponse(BaseModel):
    """Complete response for IV surface endpoint."""
    
    ticker: str = Field(..., description="Stock ticker symbol")
    spot_price: float = Field(..., description="Current spot price of underlying")
    risk_free_rate: float = Field(..., description="Risk-free interest rate used")
    
    calls: List[OptionContractIV] = Field(
        ...,
        description="Call options with calculated IVs"
    )
    puts: List[OptionContractIV] = Field(
        ...,
        description="Put options with calculated IVs"
    )
    
    metrics: IVSurfaceMetrics = Field(
        ...,
        description="Summary metrics and statistics"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "ticker": "AAPL",
                "spot_price": 250.48,
                "risk_free_rate": 0.045,
                "calls": [
                    {
                        "strike": 250.0,
                        "moneyness": 0.998,
                        "time_to_expiry": 0.00274,
                        "bid": 3.0,
                        "ask": 3.2,
                        "mid_price": 3.1,
                        "volume": 1523,
                        "open_interest": 5678,
                        "implied_volatility": 0.543,
                        "expiration": "2025-10-17"
                    }
                ],
                "puts": [],
                "metrics": {
                    "atm_call_iv": 0.543,
                    "atm_put_iv": 0.350,
                    "atm_iv_avg": 0.447,
                    "put_call_skew": 0.159,
                    "total_call_contracts": 46,
                    "total_put_contracts": 40,
                    "successful_call_ivs": 15,
                    "successful_put_ivs": 9,
                    "expiration_dates": ["2025-10-17"]
                }
            }
        }


class IVSurfaceError(BaseModel):
    """Error response for IV surface endpoint."""
    
    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Detailed error message")
    ticker: Optional[str] = Field(None, description="Ticker that caused the error")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "InvalidTicker",
                "message": "Ticker 'INVALID' not found or has no options data",
                "ticker": "INVALID"
            }
        }
