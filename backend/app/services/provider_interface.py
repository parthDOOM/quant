"""
Data Provider Interface - Abstract Base Class for Market Data Providers

This module defines the contract that all data providers must implement,
enabling clean separation of concerns and easy provider switching.

Architecture:
- DataProviderInterface: ABC defining required methods
- Implementations: PolygonProvider, YFinanceProvider
- Dependency Injection: FastAPI injects concrete provider based on config
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd


class DataProviderError(Exception):
    """Base exception for data provider errors"""
    pass


class DataProviderInterface(ABC):
    """
    Abstract interface for market data providers.
    
    All data providers (Polygon.io, yfinance, etc.) must implement this interface
    to ensure consistent behavior across the application.
    """
    
    @abstractmethod
    async def get_historical_prices(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch historical adjusted closing prices for given tickers.
        
        Args:
            tickers: List of ticker symbols (e.g., ['AAPL', 'MSFT'])
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            **kwargs: Provider-specific parameters
            
        Returns:
            DataFrame with adjusted closing prices:
                - Index: DatetimeIndex (trading dates)
                - Columns: Ticker symbols
                - Values: Adjusted closing prices
                
        Raises:
            DataProviderError: If fetching fails
        """
        pass
    
    @abstractmethod
    async def get_options_chain(
        self,
        ticker: str,
        expiration_date: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Fetch options chain for a given ticker.
        
        Args:
            ticker: Ticker symbol (e.g., 'AAPL')
            expiration_date: Optional specific expiration (YYYY-MM-DD)
            **kwargs: Provider-specific parameters
            
        Returns:
            Dictionary containing:
                - ticker: str
                - spot_price: float
                - risk_free_rate: float
                - calls: pd.DataFrame (all call options)
                - puts: pd.DataFrame (all put options)
                - expiration_dates: List[str]
                
        Raises:
            DataProviderError: If fetching fails
        """
        pass
    
    @abstractmethod
    async def get_current_price(
        self,
        ticker: str,
        **kwargs
    ) -> float:
        """
        Fetch current/latest price for a ticker.
        
        Args:
            ticker: Ticker symbol
            **kwargs: Provider-specific parameters
            
        Returns:
            Current price (most recent close)
            
        Raises:
            DataProviderError: If fetching fails
        """
        pass
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Return the name of the provider (e.g., 'polygon', 'yfinance')"""
        pass
    
    @property
    @abstractmethod
    def supports_options(self) -> bool:
        """Return True if provider supports options data"""
        pass
    
    @property
    @abstractmethod
    def supports_realtime(self) -> bool:
        """Return True if provider supports real-time/streaming data"""
        pass


class FallbackDataProvider:
    """
    Fallback strategy wrapper that tries primary provider first,
    then falls back to secondary provider on failure.
    
    Usage:
        primary = PolygonProvider()
        fallback = YFinanceProvider()
        provider = FallbackDataProvider(primary, fallback)
        
        # Will try Polygon first, fall back to yfinance if it fails
        data = await provider.get_historical_prices(['AAPL'], '2024-01-01', '2024-12-31')
    """
    
    def __init__(
        self,
        primary: DataProviderInterface,
        fallback: DataProviderInterface
    ):
        self.primary = primary
        self.fallback = fallback
        
    async def get_historical_prices(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        **kwargs
    ) -> pd.DataFrame:
        """Try primary provider first, fall back to secondary on error"""
        try:
            return await self.primary.get_historical_prices(
                tickers, start_date, end_date, **kwargs
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Primary provider ({self.primary.name}) failed: {str(e)}. "
                f"Falling back to {self.fallback.name}"
            )
            return await self.fallback.get_historical_prices(
                tickers, start_date, end_date, **kwargs
            )
    
    async def get_options_chain(
        self,
        ticker: str,
        expiration_date: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """Try primary provider first, fall back to secondary on error"""
        try:
            return await self.primary.get_options_chain(
                ticker, expiration_date, **kwargs
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Primary provider ({self.primary.name}) failed: {str(e)}. "
                f"Falling back to {self.fallback.name}"
            )
            return await self.fallback.get_options_chain(
                ticker, expiration_date, **kwargs
            )
    
    async def get_current_price(
        self,
        ticker: str,
        **kwargs
    ) -> float:
        """Try primary provider first, fall back to secondary on error"""
        try:
            return await self.primary.get_current_price(ticker, **kwargs)
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.warning(
                f"Primary provider ({self.primary.name}) failed: {str(e)}. "
                f"Falling back to {self.fallback.name}"
            )
            return await self.fallback.get_current_price(ticker, **kwargs)
    
    @property
    def name(self) -> str:
        return f"{self.primary.name}+{self.fallback.name}"
    
    @property
    def supports_options(self) -> bool:
        return self.primary.supports_options or self.fallback.supports_options
    
    @property
    def supports_realtime(self) -> bool:
        return self.primary.supports_realtime or self.fallback.supports_realtime
