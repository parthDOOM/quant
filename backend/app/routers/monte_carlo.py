"""Monte Carlo simulation API endpoints."""
from fastapi import APIRouter, HTTPException, Depends
from app.models.monte_carlo import MonteCarloRequest, MonteCarloResponse
from pydantic import BaseModel

from app.services.monte_carlo_service import MonteCarloService
from app.services.data_ingestion import fetch_and_process_prices
from app.services.provider_factory import get_data_provider
from app.services.provider_interface import DataProviderInterface
from pydantic import BaseModel, Field
from typing import List
import logging
import time

router = APIRouter(prefix="/monte-carlo", tags=["Monte Carlo"])
logger = logging.getLogger(__name__)

# Date range endpoint models and route (must be after router is defined)
class DateRangeRequest(BaseModel):
    tickers: list[str]

class DateRangeResponse(BaseModel):
    min_date: str
    max_date: str

@router.post("/date-range", response_model=DateRangeResponse)
async def get_date_range(
    request: DateRangeRequest,
    provider: DataProviderInterface = Depends(get_data_provider)
):
    """
    Return the min/max available dates for all tickers using the current provider.
    """
    import pandas as pd
    from datetime import datetime
    try:
        # Fetch data for all tickers with a wide date range
        # Use a very early start and today as end
        start = "1980-01-01"
        end = datetime.today().strftime("%Y-%m-%d")
        prices = await provider.get_historical_prices(
            tickers=request.tickers,
            start_date=start,
            end_date=end
        )
        if prices.empty:
            raise HTTPException(400, "No data found for any ticker")
        # Find intersection of available dates for all tickers
        valid = prices.dropna(axis=0, how='any')
        if valid.empty:
            raise HTTPException(400, "No overlapping dates for all tickers")
        min_date = valid.index.min().strftime("%Y-%m-%d")
        max_date = valid.index.max().strftime("%Y-%m-%d")
        return DateRangeResponse(min_date=min_date, max_date=max_date)
    except Exception as e:
        raise HTTPException(500, f"Failed to get date range: {str(e)}")


class SimpleMonteCarloRequest(BaseModel):
    """Simplified Monte Carlo request with data fetching."""
    tickers: List[str] = Field(..., min_length=1, description="List of ticker symbols")
    start_date: str = Field(..., description="Start date (YYYY-MM-DD)")
    end_date: str = Field(..., description="End date (YYYY-MM-DD)")
    num_simulations: int = Field(10000, ge=100, le=100000, description="Number of simulation paths")
    num_days: int = Field(252, ge=1, le=1000, description="Forecast days (252 = 1 year)")
    weighting: str = Field('equal', description="Portfolio weighting method: 'equal' or 'min_var'", pattern='^(equal|min_var)$')


@router.post("/simulate", response_model=MonteCarloResponse)
async def simulate_portfolio_simple(
    request: SimpleMonteCarloRequest,
    provider: DataProviderInterface = Depends(get_data_provider)
):
    """
    Run Monte Carlo simulation with automatic data fetching.
    
    Fetches historical data, calculates returns and covariance, then runs
    C++ Monte Carlo simulation (9-11x faster than pure Python).
    """
    try:
        start_time = time.time()
        
        # Fetch and process historical data
        logger.info(f"Fetching data for {len(request.tickers)} tickers...")
        data = await fetch_and_process_prices(
            request.tickers,
            request.start_date,
            request.end_date,
            provider
        )
        
        if data is None or data.empty:
            raise HTTPException(400, "No data retrieved for specified tickers and date range")
        
        # Check all tickers are present
        missing_tickers = set(request.tickers) - set(data.columns)
        if missing_tickers:
            raise HTTPException(400, f"No data found for tickers: {', '.join(missing_tickers)}")
        
        logger.info(f"Retrieved data for tickers: {list(data.columns)}")
        
        # Calculate returns
        returns = data.pct_change().dropna()
        
        if len(returns) < 30:
            raise HTTPException(400, f"Insufficient data: only {len(returns)} days. Need at least 30.")
        
        # Calculate statistics
        mean_returns = returns.mean().values  # Daily mean returns
        cov_matrix = returns.cov().values.tolist()  # Covariance matrix
        initial_prices = data.iloc[-1].values.tolist()  # Latest prices
        
        logger.info(f"Data processed: {len(returns)} days of returns")
        logger.info(f"Initial prices: {initial_prices}")
        logger.info(f"Mean returns: {mean_returns.tolist()}")
        logger.info(f"Cov matrix shape: {len(cov_matrix)}x{len(cov_matrix[0]) if cov_matrix else 0}")
        


        # Determine portfolio weights
        portfolio_weights = None
        if hasattr(request, 'weighting') and request.weighting == 'min_var':
            # Minimum-variance weights: w = inv(cov) 1 / (1^T inv(cov) 1)
            import numpy as np
            cov = np.array(cov_matrix)
            ones = np.ones(len(request.tickers))
            try:
                inv_cov = np.linalg.pinv(cov)
                raw_weights = inv_cov @ ones
                portfolio_weights = raw_weights / (ones @ inv_cov @ ones)
                portfolio_weights = portfolio_weights.tolist()
                logger.info(f"[MC] Min-var weights: {portfolio_weights}")
            except Exception as e:
                logger.warning(f"Failed to compute min-var weights, falling back to equal: {e}")
                portfolio_weights = None
        # If not min_var or failed, use equal weights
        if portfolio_weights is None:
            portfolio_weights = (np.ones(len(request.tickers)) / len(request.tickers)).tolist()
            logger.info(f"[MC] Equal weights: {portfolio_weights}")

        # Log all simulation inputs for debugging
        logger.info(f"[MC] mean_returns: {mean_returns.tolist()}")
        logger.info(f"[MC] cov_matrix: {cov_matrix}")
        logger.info(f"[MC] initial_prices: {initial_prices}")

        # Run simulation
        result = MonteCarloService.simulate_portfolio(
            tickers=request.tickers,
            initial_prices=initial_prices,
            expected_returns=mean_returns.tolist(),
            covariance_matrix=cov_matrix,
            num_simulations=request.num_simulations,
            num_days=request.num_days,
            portfolio_weights=portfolio_weights
        )
        result['portfolio_weights'] = portfolio_weights
        # Add simulation inputs for debugging
        # Also return the raw price data for debugging
        result['debug_inputs'] = {
            'mean_returns': mean_returns.tolist() if hasattr(mean_returns, 'tolist') else mean_returns,
            'cov_matrix': cov_matrix,
            'initial_prices': initial_prices,
            'portfolio_weights': portfolio_weights,
            'raw_prices': data.to_dict() if data is not None else None
        }
        
        # Add execution time
        execution_time = (time.time() - start_time) * 1000  # Convert to ms
        result['execution_time_ms'] = execution_time
        
        logger.info(f"Simulation completed in {execution_time:.2f}ms")
        
        return result
        
    except HTTPException:
        raise
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(400, f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Simulation error: {str(e)}", exc_info=True)
        raise HTTPException(500, f"Simulation failed: {str(e)}")


@router.post("/simulate-advanced", response_model=MonteCarloResponse)
async def simulate_portfolio(request: MonteCarloRequest):
    """
    Run Monte Carlo simulation for portfolio.
    
    Uses C++ implementation for 10-100x faster performance than pure Python.
    Simulates correlated asset price paths using geometric Brownian motion.
    """
    try:
        # Validate input dimensions
        n = len(request.tickers)
        if len(request.initial_prices) != n:
            raise HTTPException(400, "initial_prices length must match tickers")
        if len(request.expected_returns) != n:
            raise HTTPException(400, "expected_returns length must match tickers")
        if len(request.covariance_matrix) != n or any(len(row) != n for row in request.covariance_matrix):
            raise HTTPException(400, "covariance_matrix must be n x n")
        
        # Run simulation
        result = MonteCarloService.simulate_portfolio(
            tickers=request.tickers,
            initial_prices=request.initial_prices,
            expected_returns=request.expected_returns,
            covariance_matrix=request.covariance_matrix,
            num_simulations=request.num_simulations,
            num_days=request.num_days
        )
        
        logger.info(f"Monte Carlo simulation completed: {request.num_simulations} sims x {request.num_days} days")
        
        return result
        
    except ValueError as e:
        logger.error(f"Validation error: {str(e)}")
        raise HTTPException(400, f"Invalid input: {str(e)}")
    except Exception as e:
        logger.error(f"Simulation error: {str(e)}")
        raise HTTPException(500, f"Simulation failed: {str(e)}")


@router.get("/health")
async def health_check():
    """Check if Monte Carlo C++ module is loaded."""
    try:
        import sys
        sys.path.insert(0, 'backend/app/services')
        import core_cpp
        return {
            "status": "healthy",
            "cpp_module": "loaded",
            "message": "Monte Carlo C++ engine ready"
        }
    except ImportError as e:
        return {
            "status": "unhealthy",
            "cpp_module": "not_loaded",
            "error": str(e)
        }
