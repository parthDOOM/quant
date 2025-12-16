"""
Options Chain Data Ingestion Service

This module provides functionality to fetch and process options chain data
for a given ticker symbol using configurable data providers (Polygon.io, yfinance).

Key features:
- Fetch complete options chain (calls and puts)
- Get current spot price
- Extract dynamic risk-free rate from U.S. Treasury
- Structure data for implied volatility calculation
- Support for multiple data providers with fallback
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import yfinance as yf

from app.services.provider_interface import DataProviderInterface
from app.services.economic_data import get_risk_free_rate

logger = logging.getLogger(__name__)


class OptionsDataService:
    """Service for fetching and processing options chain data"""

    # Default risk-free rate (US 3-month Treasury Bill rate as of Oct 2025)
    DEFAULT_RISK_FREE_RATE = 0.045  # 4.5%

    @staticmethod
    async def fetch_spot_price(ticker: str, provider: DataProviderInterface) -> float:
        """
        Fetch the current spot price for the underlying asset.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'SPY')
            provider: Data provider instance (Polygon, yfinance, or Fallback)

        Returns:
            Current spot price (most recent close)

        Raises:
            ValueError: If ticker is invalid or no data available
        """
        try:
            spot_price = await provider.get_current_price(ticker)
            logger.info(f"Fetched spot price for {ticker}: ${spot_price:.2f} using {provider.name}")
            return spot_price
            
        except Exception as e:
            logger.error(f"Error fetching spot price for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch spot price for {ticker}: {str(e)}")

    @staticmethod
    async def fetch_options_chain(ticker: str, provider: DataProviderInterface) -> Dict:
        """
        Fetch the complete options chain for a given ticker.

        This method retrieves all available options contracts (both calls and puts)
        across all expiration dates, along with the current spot price and risk-free rate.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'SPY')
            provider: Data provider instance (Polygon, yfinance, or Fallback)

        Returns:
            Dictionary containing:
                - ticker: str - Ticker symbol
                - spot_price: float - Current underlying price
                - risk_free_rate: float - Risk-free rate proxy
                - calls: pd.DataFrame - All call options
                - puts: pd.DataFrame - All put options
                - expiration_dates: List[str] - Available expiration dates

        Raises:
            ValueError: If ticker is invalid or no options data available
        """
        try:
            logger.info(f"Fetching options chain for {ticker} using {provider.name}")
            
            # Get spot price via provider
            spot_price = await OptionsDataService.fetch_spot_price(ticker, provider)
            
            # Get options chain via provider
            options_data = await provider.get_options_chain(ticker)
            
            if not options_data or 'expiration_dates' not in options_data:
                raise ValueError(f"No options data available for ticker: {ticker}")
            
            expiration_dates = options_data['expiration_dates']
            logger.info(f"Found {len(expiration_dates)} expiration dates for {ticker}")
            
            # Extract calls and puts from provider response
            calls_df = options_data.get('calls', pd.DataFrame())
            puts_df = options_data.get('puts', pd.DataFrame())
            
            if calls_df.empty and puts_df.empty:
                raise ValueError(f"No valid options data retrieved for ticker: {ticker}")
            
            # Clean and validate data
            if not calls_df.empty:
                calls_df = OptionsDataService._clean_options_data(calls_df, spot_price)
            if not puts_df.empty:
                puts_df = OptionsDataService._clean_options_data(puts_df, spot_price)
            
            # Fetch dynamic risk-free rate from U.S. Treasury
            # Falls back to DEFAULT_RISK_FREE_RATE if API fails
            risk_free_rate = await get_risk_free_rate()
            
            logger.info(
                f"Successfully fetched {len(calls_df)} calls and {len(puts_df)} puts for {ticker}, "
                f"risk-free rate: {risk_free_rate:.4f}"
            )
            
            return {
                'ticker': ticker,
                'spot_price': spot_price,
                'risk_free_rate': risk_free_rate,
                'calls': calls_df,
                'puts': puts_df,
                'expiration_dates': expiration_dates
            }
            
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error fetching options chain for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch options chain for {ticker}: {str(e)}")

    @staticmethod
    def _clean_options_data(df: pd.DataFrame, spot_price: float) -> pd.DataFrame:
        """
        Clean and validate options data.

        Removes contracts with:
        - Zero or NaN bid/ask prices
        - Zero volume (no trading activity)
        - Extremely low liquidity

        Adds calculated fields:
        - moneyness: strike / spot_price
        - mid_price: (bid + ask) / 2
        - time_to_expiry: years until expiration

        Args:
            df: Raw options DataFrame
            spot_price: Current spot price

        Returns:
            Cleaned DataFrame with additional calculated fields
        """
        if df.empty:
            return df
        
        # Make a copy to avoid modifying original
        df = df.copy()
        
        # Filter out invalid contracts
        df = df[
            (df['bid'] > 0) &
            (df['ask'] > 0) &
            (df['volume'] > 0) &
            (df['bid'].notna()) &
            (df['ask'].notna())
        ]
        
        # Calculate mid price
        df['mid_price'] = (df['bid'] + df['ask']) / 2
        
        # Calculate moneyness (strike / spot)
        df['moneyness'] = df['strike'] / spot_price
        
        # Calculate time to expiry (in years)
        df['time_to_expiry'] = df['expiration'].apply(
            lambda x: OptionsDataService._calculate_time_to_expiry(x)
        )
        
        # Sort by expiration and strike
        df = df.sort_values(['expiration', 'strike']).reset_index(drop=True)
        
        return df

    @staticmethod
    def _calculate_time_to_expiry(expiration_str: str) -> float:
        """
        Calculate time to expiry in years.

        Args:
            expiration_str: Expiration date as string (YYYY-MM-DD)

        Returns:
            Time to expiry in years (e.g., 0.25 for 3 months)
        """
        try:
            exp_date = datetime.strptime(expiration_str, '%Y-%m-%d')
            today = datetime.now()
            days_to_expiry = (exp_date - today).days
            
            # Ensure minimum of 1 day to avoid division issues
            days_to_expiry = max(days_to_expiry, 1)
            
            # Convert to years (assuming 365 days per year)
            years_to_expiry = days_to_expiry / 365.0
            
            return years_to_expiry
            
        except Exception as e:
            logger.warning(f"Error calculating time to expiry for {expiration_str}: {str(e)}")
            return 0.0

    @staticmethod
    def get_options_summary(options_data: Dict) -> Dict:
        """
        Generate summary statistics for options chain data.

        Args:
            options_data: Options chain data from fetch_options_chain()

        Returns:
            Dictionary with summary statistics:
                - total_calls: Number of call contracts
                - total_puts: Number of put contracts
                - date_range: Earliest and latest expiration dates
                - strike_range: Min and max strike prices
                - avg_volume: Average trading volume
        """
        calls_df = options_data['calls']
        puts_df = options_data['puts']
        
        summary = {
            'ticker': options_data['ticker'],
            'spot_price': options_data['spot_price'],
            'total_calls': len(calls_df),
            'total_puts': len(puts_df),
            'expiration_dates_count': len(options_data['expiration_dates']),
            'earliest_expiration': min(options_data['expiration_dates']),
            'latest_expiration': max(options_data['expiration_dates']),
        }
        
        if not calls_df.empty:
            summary.update({
                'calls_strike_range': {
                    'min': float(calls_df['strike'].min()),
                    'max': float(calls_df['strike'].max())
                },
                'calls_avg_volume': float(calls_df['volume'].mean()),
            })
        
        if not puts_df.empty:
            summary.update({
                'puts_strike_range': {
                    'min': float(puts_df['strike'].min()),
                    'max': float(puts_df['strike'].max())
                },
                'puts_avg_volume': float(puts_df['volume'].mean()),
            })
        
        return summary
