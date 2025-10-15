"""
IV Surface API Router.

Provides endpoints for fetching and calculating implied volatility surface data
for options chains. Used by the frontend 3D visualization.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Literal
import logging
import pandas as pd
import numpy as np

from app.models.iv_surface import (
    IVSurfaceResponse,
    IVSurfaceError,
    OptionContractIV,
    IVSurfaceMetrics
)
from app.services.options_data import OptionsDataService
from app.services.implied_volatility import ImpliedVolatilityCalculator

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/iv",
    tags=["Implied Volatility Surface"],
    responses={
        404: {"model": IVSurfaceError, "description": "Ticker not found"},
        500: {"model": IVSurfaceError, "description": "Internal server error"}
    }
)


def _filter_by_expiration(
    options_df: pd.DataFrame,
    expiration_filter: str
) -> pd.DataFrame:
    """
    Filter options by expiration date.
    
    Args:
        options_df: DataFrame with 'expiration' and 'time_to_expiry' columns
        expiration_filter: 'first', 'near_term', or 'all'
        
    Returns:
        Filtered DataFrame
    """
    if len(options_df) == 0:
        return options_df.copy()
    
    if expiration_filter == 'first':
        # Only the nearest expiration
        first_exp = options_df['expiration'].min()
        return options_df[options_df['expiration'] == first_exp].copy()
    
    elif expiration_filter == 'near_term':
        # Expirations within 90 days
        return options_df[options_df['time_to_expiry'] <= 90/365].copy()
    
    else:  # 'all'
        return options_df.copy()


def _filter_by_volume(
    options_df: pd.DataFrame,
    min_volume: int
) -> pd.DataFrame:
    """
    Filter options by minimum volume.
    
    Args:
        options_df: DataFrame with 'volume' column
        min_volume: Minimum volume threshold
        
    Returns:
        Filtered DataFrame
    """
    if min_volume > 0:
        return options_df[options_df['volume'] >= min_volume].copy()
    return options_df.copy()


def _calculate_metrics(
    calls_with_iv: pd.DataFrame,
    puts_with_iv: pd.DataFrame,
    spot_price: float
) -> IVSurfaceMetrics:
    """
    Calculate summary metrics for the IV surface.
    
    Args:
        calls_with_iv: DataFrame with calculated IVs for calls
        puts_with_iv: DataFrame with calculated IVs for puts
        spot_price: Current spot price
        
    Returns:
        IVSurfaceMetrics with calculated statistics
    """
    # Filter to valid IVs
    calls_valid = calls_with_iv[calls_with_iv['calculated_iv'].notna()].copy()
    puts_valid = puts_with_iv[puts_with_iv['calculated_iv'].notna()].copy()
    
    # ATM volatility (closest to moneyness = 1.0)
    atm_call_iv = None
    atm_put_iv = None
    atm_iv_avg = None
    
    if len(calls_valid) > 0:
        atm_idx = (calls_valid['moneyness'] - 1.0).abs().idxmin()
        atm_call_iv = float(calls_valid.loc[atm_idx, 'calculated_iv'])
    
    if len(puts_valid) > 0:
        atm_idx = (puts_valid['moneyness'] - 1.0).abs().idxmin()
        atm_put_iv = float(puts_valid.loc[atm_idx, 'calculated_iv'])
    
    if atm_call_iv is not None and atm_put_iv is not None:
        atm_iv_avg = (atm_call_iv + atm_put_iv) / 2
    elif atm_call_iv is not None:
        atm_iv_avg = atm_call_iv
    elif atm_put_iv is not None:
        atm_iv_avg = atm_put_iv
    
    # Skew calculation (OTM put IV - OTM call IV)
    put_call_skew = None
    if len(calls_valid) > 0 and len(puts_valid) > 0:
        otm_calls = calls_valid[calls_valid['moneyness'] > 1.05]
        otm_puts = puts_valid[puts_valid['moneyness'] < 0.95]
        
        if len(otm_calls) > 0 and len(otm_puts) > 0:
            avg_otm_call_iv = otm_calls['calculated_iv'].mean()
            avg_otm_put_iv = otm_puts['calculated_iv'].mean()
            put_call_skew = float(avg_otm_put_iv - avg_otm_call_iv)
    
    # IV ranges (handle NaN/inf carefully for JSON serialization)
    iv_range_calls = None
    if len(calls_valid) > 0:
        std_val = calls_valid['calculated_iv'].std()
        iv_range_calls = {
            'min': float(calls_valid['calculated_iv'].min()),
            'max': float(calls_valid['calculated_iv'].max()),
            'mean': float(calls_valid['calculated_iv'].mean()),
            'std': float(std_val) if pd.notna(std_val) and not np.isinf(std_val) else 0.0
        }
    
    iv_range_puts = None
    if len(puts_valid) > 0:
        std_val = puts_valid['calculated_iv'].std()
        iv_range_puts = {
            'min': float(puts_valid['calculated_iv'].min()),
            'max': float(puts_valid['calculated_iv'].max()),
            'mean': float(puts_valid['calculated_iv'].mean()),
            'std': float(std_val) if pd.notna(std_val) and not np.isinf(std_val) else 0.0
        }
    
    # Expiration dates
    all_expirations = sorted(
        set(calls_with_iv['expiration'].tolist() + puts_with_iv['expiration'].tolist())
    )
    
    return IVSurfaceMetrics(
        atm_call_iv=atm_call_iv,
        atm_put_iv=atm_put_iv,
        atm_iv_avg=atm_iv_avg,
        put_call_skew=put_call_skew,
        iv_range_calls=iv_range_calls,
        iv_range_puts=iv_range_puts,
        total_call_contracts=len(calls_with_iv),
        total_put_contracts=len(puts_with_iv),
        successful_call_ivs=len(calls_valid),
        successful_put_ivs=len(puts_valid),
        expiration_dates=all_expirations
    )


def _dataframe_to_contracts(df: pd.DataFrame) -> list[OptionContractIV]:
    """
    Convert DataFrame to list of OptionContractIV models.
    
    Args:
        df: DataFrame with option data and calculated_iv column
        
    Returns:
        List of OptionContractIV models
    """
    contracts = []
    
    for _, row in df.iterrows():
        contract = OptionContractIV(
            strike=float(row['strike']),
            moneyness=float(row['moneyness']),
            time_to_expiry=float(row['time_to_expiry']),
            bid=float(row['bid']),
            ask=float(row['ask']),
            mid_price=float(row['mid_price']),
            volume=int(row['volume']),
            open_interest=int(row['openInterest']),
            implied_volatility=float(row['calculated_iv']) if pd.notna(row['calculated_iv']) else None,
            expiration=str(row['expiration'])
        )
        contracts.append(contract)
    
    return contracts


@router.get(
    "/surface/{ticker}",
    response_model=IVSurfaceResponse,
    summary="Get implied volatility surface data",
    description=(
        "Fetches options chain for the specified ticker, calculates implied "
        "volatility for each contract using Black-Scholes-Merton model and "
        "Newton-Raphson solver, and returns data suitable for 3D surface visualization."
    )
)
async def get_iv_surface(
    ticker: str,
    expiration_filter: Literal['first', 'near_term', 'all'] = Query(
        default='first',
        description=(
            "Filter expirations: 'first' (nearest only), "
            "'near_term' (within 90 days), 'all' (all available)"
        )
    ),
    min_volume: int = Query(
        default=10,
        ge=0,
        description="Minimum volume filter for contracts"
    )
) -> IVSurfaceResponse:
    """
    Get implied volatility surface data for a ticker.
    
    This endpoint:
    1. Fetches the complete options chain from yfinance
    2. Filters based on expiration and volume criteria
    3. Calculates implied volatility using Newton-Raphson solver
    4. Computes surface metrics (ATM IV, skew, term structure)
    5. Returns structured data for 3D visualization
    
    **Note:** Deep ITM/OTM options may not have calculated IVs due to
    numerical instability (low Vega). This is expected behavior.
    """
    ticker = ticker.upper().strip()
    
    logger.info(
        f"Fetching IV surface for {ticker} "
        f"(expiration_filter={expiration_filter}, min_volume={min_volume})"
    )
    
    try:
        # Step 1: Fetch options chain
        logger.info(f"Fetching options chain for {ticker}...")
        options_data = OptionsDataService.fetch_options_chain(ticker)
        
        spot_price = options_data['spot_price']
        risk_free_rate = options_data['risk_free_rate']
        calls = options_data['calls']
        puts = options_data['puts']
        
        logger.info(
            f"Fetched {len(calls)} calls and {len(puts)} puts "
            f"across {len(options_data['expiration_dates'])} expirations"
        )
        
        # Step 2: Apply filters
        logger.info("Applying filters...")
        calls_filtered = _filter_by_expiration(calls, expiration_filter)
        puts_filtered = _filter_by_expiration(puts, expiration_filter)
        
        calls_filtered = _filter_by_volume(calls_filtered, min_volume)
        puts_filtered = _filter_by_volume(puts_filtered, min_volume)
        
        logger.info(
            f"After filtering: {len(calls_filtered)} calls, {len(puts_filtered)} puts"
        )
        
        if len(calls_filtered) == 0 and len(puts_filtered) == 0:
            raise HTTPException(
                status_code=404,
                detail=f"No options data found for {ticker} with the specified filters"
            )
        
        # Step 3: Calculate implied volatility
        logger.info("Calculating implied volatility for calls...")
        calls_with_iv = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            calls_filtered,
            spot_price,
            risk_free_rate,
            'call'
        )
        
        logger.info("Calculating implied volatility for puts...")
        puts_with_iv = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            puts_filtered,
            spot_price,
            risk_free_rate,
            'put'
        )
        
        # Step 4: Calculate metrics
        logger.info("Calculating surface metrics...")
        metrics = _calculate_metrics(calls_with_iv, puts_with_iv, spot_price)
        
        logger.info(
            f"IV calculation complete: "
            f"{metrics.successful_call_ivs}/{metrics.total_call_contracts} calls, "
            f"{metrics.successful_put_ivs}/{metrics.total_put_contracts} puts"
        )
        
        # Step 5: Convert to response models
        call_contracts = _dataframe_to_contracts(calls_with_iv)
        put_contracts = _dataframe_to_contracts(puts_with_iv)
        
        response = IVSurfaceResponse(
            ticker=ticker,
            spot_price=spot_price,
            risk_free_rate=risk_free_rate,
            calls=call_contracts,
            puts=put_contracts,
            metrics=metrics
        )
        
        logger.info(f"Successfully generated IV surface for {ticker}")
        return response
        
    except HTTPException:
        raise
    
    except ValueError as e:
        logger.error(f"Invalid data for {ticker}: {e}")
        raise HTTPException(
            status_code=404,
            detail=f"Could not fetch options data for {ticker}: {str(e)}"
        )
    
    except Exception as e:
        logger.error(f"Error generating IV surface for {ticker}: {e}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail=f"Internal error processing {ticker}: {str(e)}"
        )


@router.get(
    "/health",
    summary="Health check for IV surface service",
    description="Simple health check endpoint to verify the IV calculation service is running"
)
async def health_check():
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "implied_volatility_surface",
        "capabilities": [
            "options_chain_fetching",
            "black_scholes_pricing",
            "newton_raphson_iv_solver",
            "surface_metrics_calculation"
        ]
    }
