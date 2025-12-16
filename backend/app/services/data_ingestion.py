"""
Data ingestion and processing service for financial market data.
Handles fetching historical prices and calculating returns and correlations.
Supports multiple data providers (Polygon.io, yfinance) with automatic fallback.
"""
import pandas as pd
import numpy as np
import yfinance as yf
from typing import List, Tuple, Dict
from datetime import datetime
import logging

from app.config import get_settings
from app.services.provider_interface import DataProviderInterface

logger = logging.getLogger(__name__)
settings = get_settings()


class DataIngestionError(Exception):
    """Custom exception for data ingestion errors."""
    pass


class InsufficientDataError(Exception):
    """Raised when there's insufficient data to perform calculations."""
    pass


async def fetch_and_process_prices(
    tickers: List[str],
    start_date: str,
    end_date: str,
    provider: DataProviderInterface
) -> pd.DataFrame:
    """
    Fetch historical adjusted closing prices and calculate daily returns.
    
    Args:
        tickers: List of ticker symbols
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        
    Returns:
        DataFrame with daily percentage returns (tickers as columns, dates as index)
        
    Raises:
        DataIngestionError: If data fetching fails
        InsufficientDataError: If insufficient data is available
    """
    logger.info(f"Fetching data for {len(tickers)} tickers from {start_date} to {end_date} using {provider.name}")
    
    try:
        # Fetch data via provider interface (async call)
        # Provider returns DataFrame with tickers as columns, dates as index (adjusted close prices)
        prices = await provider.get_historical_prices(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date
        )
        
        if prices.empty:
            raise InsufficientDataError(
                f"No data available for the specified tickers and date range"
            )
        
        # Drop columns with all NaN values
        prices = prices.dropna(axis=1, how='all')
        
        # Note: We allow single ticker here (data fetching level)
        # The minimum ticker requirement (2+) is enforced at API level via Pydantic models
        if prices.shape[1] < 1:
            raise InsufficientDataError(
                f"No valid tickers remain after data cleaning"
            )
        
        logger.info(f"Successfully fetched {prices.shape[0]} days of data for {prices.shape[1]} tickers")
        
        # Calculate daily percentage returns
        returns = prices.pct_change()
        
        # Drop the first row (which will be NaN)
        returns = returns.dropna(how='all')
        
        # Drop any remaining rows with NaN values
        returns = returns.dropna()
        
        if returns.empty or len(returns) < 10:
            raise InsufficientDataError(
                f"Insufficient data points after cleaning. Got {len(returns)} days, need at least 10"
            )
        
        logger.info(f"Calculated returns for {len(returns)} trading days")
        
        return returns
        
    except Exception as e:
        if isinstance(e, (DataIngestionError, InsufficientDataError)):
            raise
        logger.error(f"Error fetching data: {str(e)}")
        raise DataIngestionError(f"Failed to fetch market data: {str(e)}")


def calculate_correlation_matrix(
    returns: pd.DataFrame,
    min_periods: float = None
) -> pd.DataFrame:
    """
    Calculate Pearson correlation matrix from returns data.
    
    Args:
        returns: DataFrame of daily returns
        min_periods: Minimum number of observations required per pair.
                    If None, uses the configured threshold from settings.
                    
    Returns:
        Correlation matrix as DataFrame
        
    Raises:
        InsufficientDataError: If insufficient overlapping data
    """
    if min_periods is None:
        # Use configured percentage of total observations
        min_periods = int(len(returns) * settings.min_correlation_periods)
    
    logger.info(f"Calculating correlation matrix with min_periods={min_periods}")
    
    # Calculate correlation matrix
    correlation_matrix = returns.corr(method='pearson', min_periods=min_periods)
    
    # Check for NaN values in the correlation matrix
    if correlation_matrix.isna().any().any():
        nan_pairs = correlation_matrix.isna().sum().sum()
        logger.warning(f"Correlation matrix contains {nan_pairs} NaN values")
        raise InsufficientDataError(
            f"Insufficient overlapping data to compute correlation. "
            f"Required at least {min_periods} common observations per pair."
        )
    
    logger.info(f"Successfully calculated {correlation_matrix.shape[0]}x{correlation_matrix.shape[1]} correlation matrix")
    
    return correlation_matrix


async def get_correlation_data(
    tickers: List[str],
    start_date: str,
    end_date: str,
    provider: DataProviderInterface
) -> Tuple[pd.DataFrame, pd.DataFrame, Dict[str, any]]:
    """
    High-level function to fetch data and calculate correlation matrix.
    
    Args:
        tickers: List of ticker symbols
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        provider: Data provider instance (Polygon, yfinance, or Fallback)
        
    Returns:
        Tuple of (returns_df, correlation_matrix, metadata)
        
    Raises:
        DataIngestionError: If data fetching fails
        InsufficientDataError: If insufficient data is available
    """
    # Fetch and process price data
    returns = await fetch_and_process_prices(tickers, start_date, end_date, provider)
    
    # Calculate correlation matrix
    correlation_matrix = calculate_correlation_matrix(returns)
    
    # Prepare metadata
    metadata = {
        'actual_tickers': list(returns.columns),
        'start_date': returns.index[0].strftime('%Y-%m-%d'),
        'end_date': returns.index[-1].strftime('%Y-%m-%d'),
        'data_points': len(returns),
        'missing_tickers': list(set(tickers) - set(returns.columns))
    }
    
    logger.info(f"Correlation analysis complete. Used {metadata['data_points']} data points")
    if metadata['missing_tickers']:
        logger.warning(f"Missing data for tickers: {metadata['missing_tickers']}")
    
    return returns, correlation_matrix, metadata


async def validate_tickers_data_availability(
    tickers: List[str],
    start_date: str,
    end_date: str,
    provider: DataProviderInterface
) -> Dict[str, bool]:
    """
    Check which tickers have data available for the given date range.
    Useful for pre-validation before full data fetch.
    
    Args:
        tickers: List of ticker symbols
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        provider: Data provider instance (Polygon, yfinance, or Fallback)
        
    Returns:
        Dictionary mapping ticker to availability (True/False)
    """
    availability = {}
    
    for ticker in tickers:
        try:
            data = await provider.get_historical_prices(
                [ticker],
                start_date,
                end_date
            )
            availability[ticker] = not data.empty
        except Exception as e:
            logger.warning(f"Error checking {ticker}: {str(e)}")
            availability[ticker] = False
    
    return availability


async def fetch_prices(
    tickers: List[str],
    start_date: str,
    end_date: str,
    provider: DataProviderInterface
) -> pd.DataFrame:
    """
    Fetch historical adjusted closing prices (without calculating returns).
    
    This is a simpler version of fetch_and_process_prices that returns
    raw prices instead of returns. Useful for cointegration testing which
    requires price levels.
    
    Args:
        tickers: List of ticker symbols
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        provider: Data provider instance (Polygon, yfinance, or Fallback)
        
    Returns:
        DataFrame with daily adjusted closing prices (tickers as columns, dates as index)
        
    Raises:
        DataIngestionError: If data fetching fails
        InsufficientDataError: If insufficient data is available
    """
    logger.info(f"Fetching price data for {len(tickers)} tickers from {start_date} to {end_date} using {provider.name}")
    
    try:
        # Fetch data via provider interface (async call)
        prices = await provider.get_historical_prices(
            tickers=tickers,
            start_date=start_date,
            end_date=end_date
        )
        
        if prices.empty:
            raise InsufficientDataError(
                f"No data returned for tickers: {tickers}"
            )
        
        # Drop columns with all NaN values
        prices = prices.dropna(axis=1, how='all')
        
        # Drop rows with any NaN values (need complete data for cointegration)
        prices = prices.dropna()
        
        if prices.empty or len(prices) < 30:
            raise InsufficientDataError(
                f"Insufficient data: need at least 30 observations, got {len(prices)}"
            )
        
        logger.info(f"Successfully fetched {prices.shape[0]} days of price data for {prices.shape[1]} tickers")
        
        return prices
        
    except Exception as e:
        logger.error(f"Error fetching price data: {str(e)}")
        raise DataIngestionError(f"Failed to fetch price data: {str(e)}")
