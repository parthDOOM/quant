"""
Options Chain Data Ingestion Service

This module provides functionality to fetch and process options chain data
for a given ticker symbol using the yfinance library.

Key features:
- Fetch complete options chain (calls and puts)
- Get current spot price
- Extract risk-free rate proxy
- Structure data for implied volatility calculation
"""

import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import pandas as pd
import yfinance as yf

logger = logging.getLogger(__name__)


class OptionsDataService:
    """Service for fetching and processing options chain data"""

    # Default risk-free rate (US 3-month Treasury Bill rate as of Oct 2025)
    DEFAULT_RISK_FREE_RATE = 0.045  # 4.5%

    @staticmethod
    def fetch_spot_price(ticker: str) -> float:
        """
        Fetch the current spot price for the underlying asset.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'SPY')

        Returns:
            Current spot price (most recent close)

        Raises:
            ValueError: If ticker is invalid or no data available
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period='1d')
            
            if hist.empty:
                raise ValueError(f"No price data available for ticker: {ticker}")
            
            spot_price = float(hist['Close'].iloc[-1])
            logger.info(f"Fetched spot price for {ticker}: ${spot_price:.2f}")
            return spot_price
            
        except Exception as e:
            logger.error(f"Error fetching spot price for {ticker}: {str(e)}")
            raise ValueError(f"Failed to fetch spot price for {ticker}: {str(e)}")

    @staticmethod
    def fetch_options_chain(ticker: str) -> Dict:
        """
        Fetch the complete options chain for a given ticker.

        This method retrieves all available options contracts (both calls and puts)
        across all expiration dates, along with the current spot price and risk-free rate.

        Args:
            ticker: Stock ticker symbol (e.g., 'AAPL', 'SPY')

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
            logger.info(f"Fetching options chain for {ticker}")
            
            # Create ticker object
            ticker_obj = yf.Ticker(ticker)
            
            # Get spot price
            spot_price = OptionsDataService.fetch_spot_price(ticker)
            
            # Get available expiration dates
            expiration_dates = ticker_obj.options
            
            if not expiration_dates:
                raise ValueError(f"No options data available for ticker: {ticker}")
            
            logger.info(f"Found {len(expiration_dates)} expiration dates for {ticker}")
            
            # Fetch options data for each expiration date
            all_calls = []
            all_puts = []
            
            for exp_date in expiration_dates:
                try:
                    opt_chain = ticker_obj.option_chain(exp_date)
                    
                    # Add expiration date to each row
                    calls_df = opt_chain.calls.copy()
                    puts_df = opt_chain.puts.copy()
                    
                    calls_df['expiration'] = exp_date
                    puts_df['expiration'] = exp_date
                    
                    all_calls.append(calls_df)
                    all_puts.append(puts_df)
                    
                    logger.debug(f"Fetched {len(calls_df)} calls and {len(puts_df)} puts for {exp_date}")
                    
                except Exception as e:
                    logger.warning(f"Failed to fetch options for {ticker} expiry {exp_date}: {str(e)}")
                    continue
            
            if not all_calls or not all_puts:
                raise ValueError(f"No valid options data retrieved for ticker: {ticker}")
            
            # Concatenate all dataframes
            calls_df = pd.concat(all_calls, ignore_index=True)
            puts_df = pd.concat(all_puts, ignore_index=True)
            
            # Clean and validate data
            calls_df = OptionsDataService._clean_options_data(calls_df, spot_price)
            puts_df = OptionsDataService._clean_options_data(puts_df, spot_price)
            
            logger.info(f"Successfully fetched {len(calls_df)} calls and {len(puts_df)} puts for {ticker}")
            
            return {
                'ticker': ticker,
                'spot_price': spot_price,
                'risk_free_rate': OptionsDataService.DEFAULT_RISK_FREE_RATE,
                'calls': calls_df,
                'puts': puts_df,
                'expiration_dates': list(expiration_dates)
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
