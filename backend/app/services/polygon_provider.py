"""
Polygon.io Data Provider Implementation

Official Polygon.io API client wrapper implementing DataProviderInterface.
Provides institutional-grade market data with OPRA options data.

API Documentation: https://polygon.io/docs/
Python Client: https://github.com/polygon-io/client-python
"""

import logging
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np
from polygon import RESTClient
from polygon.rest.models import Agg, OptionsContract

from app.services.provider_interface import DataProviderInterface, DataProviderError
from app.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class PolygonProvider(DataProviderInterface):
    """
    Polygon.io API implementation of DataProviderInterface.
    
    Features:
    - Institutional-grade OPRA options data
    - High-quality adjusted historical prices
    - WebSocket support for real-time streaming
    - Clean, well-documented API
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Polygon.io client.
        
        Args:
            api_key: Polygon.io API key (defaults to settings.polygon_api_key)
        """
        self.api_key = api_key or getattr(settings, 'polygon_api_key', None)
        
        if not self.api_key:
            raise ValueError(
                "Polygon.io API key not found. "
                "Set POLYGON_API_KEY in .env or pass as argument."
            )
        
        self.client = RESTClient(api_key=self.api_key)
        logger.info(f"Initialized {self.name} provider")
    
    async def get_historical_prices(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch historical adjusted closing prices from Polygon.io.
        
        Uses Aggregates (Bars) API: https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__range__multiplier___timespan___from___to
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            **kwargs: Additional parameters (multiplier, timespan, adjusted, sort, limit)
            
        Returns:
            DataFrame with adjusted closing prices (tickers as columns, dates as index)
        """
        try:
            logger.info(
                f"Fetching {len(tickers)} tickers from Polygon.io "
                f"({start_date} to {end_date})"
            )
            
            # Polygon.io parameters
            multiplier = kwargs.get('multiplier', 1)
            timespan = kwargs.get('timespan', 'day')
            adjusted = kwargs.get('adjusted', True)
            sort = kwargs.get('sort', 'asc')
            limit = kwargs.get('limit', 50000)
            
            all_prices = {}
            failed_tickers = []
            
            for ticker in tickers:
                try:
                    # Fetch aggregates for this ticker
                    aggs = self.client.get_aggs(
                        ticker=ticker.upper(),
                        multiplier=multiplier,
                        timespan=timespan,
                        from_=start_date,
                        to=end_date,
                        adjusted=adjusted,
                        sort=sort,
                        limit=limit
                    )
                    
                    if not aggs:
                        logger.warning(f"No data returned for {ticker}")
                        failed_tickers.append(ticker)
                        continue
                    
                    # Convert to DataFrame
                    dates = []
                    prices = []
                    
                    for agg in aggs:
                        # Polygon returns millisecond timestamp
                        date = pd.Timestamp(agg.timestamp, unit='ms').date()
                        dates.append(date)
                        prices.append(agg.close)  # Use adjusted close
                    
                    if len(dates) == 0:
                        logger.warning(f"No price data for {ticker}")
                        failed_tickers.append(ticker)
                        continue
                    
                    # Create series for this ticker
                    ticker_series = pd.Series(prices, index=dates, name=ticker)
                    all_prices[ticker] = ticker_series
                    
                    logger.debug(f"Fetched {len(prices)} data points for {ticker}")
                    
                except Exception as e:
                    logger.error(f"Error fetching {ticker}: {str(e)}")
                    failed_tickers.append(ticker)
                    continue
            
            if not all_prices:
                raise DataProviderError(
                    f"Failed to fetch data for all tickers. "
                    f"Failed: {failed_tickers}"
                )
            
            # Combine into DataFrame
            df = pd.DataFrame(all_prices)
            
            # Convert index to DatetimeIndex
            df.index = pd.DatetimeIndex(df.index)
            df = df.sort_index()
            
            if failed_tickers:
                logger.warning(
                    f"Successfully fetched {len(all_prices)}/{len(tickers)} tickers. "
                    f"Failed: {failed_tickers}"
                )
            
            logger.info(
                f"Polygon.io fetch complete: {len(df)} days, "
                f"{len(df.columns)} tickers"
            )
            
            return df
            
        except Exception as e:
            logger.error(f"Polygon.io API error: {str(e)}")
            raise DataProviderError(f"Polygon.io fetch failed: {str(e)}")
    
    async def get_options_chain(
        self,
        ticker: str,
        expiration_date: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Fetch options chain from Polygon.io OPRA data.
        
        Uses Options Contracts API: https://polygon.io/docs/options/get_v3_reference_options_contracts
        
        Args:
            ticker: Underlying ticker symbol
            expiration_date: Optional specific expiration (YYYY-MM-DD)
            **kwargs: Additional filters (contract_type, strike_price, limit)
            
        Returns:
            Dictionary with structure matching yfinance for compatibility:
                - ticker: str
                - spot_price: float
                - risk_free_rate: float
                - calls: pd.DataFrame
                - puts: pd.DataFrame
                - expiration_dates: List[str]
        """
        try:
            logger.info(f"Fetching options chain for {ticker} from Polygon.io")
            
            # Get current spot price first
            spot_price = await self.get_current_price(ticker)
            
            # Fetch options contracts
            # Note: Polygon returns contracts, we need to query for each expiration
            contracts = self.client.list_options_contracts(
                underlying_ticker=ticker.upper(),
                expiration_date_gte=datetime.now().strftime('%Y-%m-%d'),
                limit=1000,
                **kwargs
            )
            
            if not contracts:
                raise DataProviderError(f"No options contracts found for {ticker}")
            
            # Group by expiration and type
            calls_data = []
            puts_data = []
            expiration_dates = set()
            
            for contract in contracts:
                exp_date = contract.expiration_date
                expiration_dates.add(exp_date)
                
                # If specific expiration requested, filter
                if expiration_date and exp_date != expiration_date:
                    continue
                
                contract_data = {
                    'strike': contract.strike_price,
                    'expiration': exp_date,
                    'contractSymbol': contract.ticker,
                    # Note: Polygon doesn't provide greeks/IV in contract listing
                    # Need separate quote call for bid/ask/volume
                }
                
                if contract.contract_type == 'call':
                    calls_data.append(contract_data)
                else:
                    puts_data.append(contract_data)
            
            # Convert to DataFrames
            calls_df = pd.DataFrame(calls_data) if calls_data else pd.DataFrame()
            puts_df = pd.DataFrame(puts_data) if puts_data else pd.DataFrame()
            
            # TODO: Fetch quotes for bid/ask/volume using last_quote endpoint
            # For now, return structure compatible with yfinance
            
            # Get risk-free rate (will be replaced by dynamic rate service)
            from app.services.options_data import OptionsDataService
            risk_free_rate = OptionsDataService.DEFAULT_RISK_FREE_RATE
            
            result = {
                'ticker': ticker,
                'spot_price': spot_price,
                'risk_free_rate': risk_free_rate,
                'calls': calls_df,
                'puts': puts_df,
                'expiration_dates': sorted(list(expiration_dates))
            }
            
            logger.info(
                f"Fetched {len(calls_df)} calls, {len(puts_df)} puts "
                f"for {ticker} ({len(expiration_dates)} expirations)"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Polygon.io options fetch error: {str(e)}")
            raise DataProviderError(f"Options fetch failed: {str(e)}")
    
    async def get_current_price(
        self,
        ticker: str,
        **kwargs
    ) -> float:
        """
        Fetch current price for a ticker.
        
        Uses Previous Close API: https://polygon.io/docs/stocks/get_v2_aggs_ticker__stocksticker__prev
        
        Args:
            ticker: Ticker symbol
            **kwargs: Additional parameters
            
        Returns:
            Current/latest closing price
        """
        try:
            # Get previous close (most recent trading day)
            agg = self.client.get_previous_close_agg(ticker.upper())
            
            if not agg or len(agg) == 0:
                raise DataProviderError(f"No price data for {ticker}")
            
            # Polygon returns list with single result
            close_price = agg[0].close
            
            logger.debug(f"Fetched current price for {ticker}: ${close_price:.2f}")
            
            return float(close_price)
            
        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {str(e)}")
            raise DataProviderError(f"Current price fetch failed: {str(e)}")
    
    @property
    def name(self) -> str:
        return "polygon"
    
    @property
    def supports_options(self) -> bool:
        return True
    
    @property
    def supports_realtime(self) -> bool:
        return True
