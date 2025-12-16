"""
Data Provider Factory

Creates and configures data provider instances based on application settings.
Implements fallback strategy and dependency injection for FastAPI endpoints.
"""

import logging
from typing import Optional
from functools import lru_cache

from app.services.provider_interface import (
    DataProviderInterface,
    FallbackDataProvider
)
from app.services.polygon_provider import PolygonProvider
from app.services.yfinance_provider import YFinanceProvider
from app.config import get_settings

logger = logging.getLogger(__name__)


class ProviderFactory:
    """
    Factory for creating data provider instances.
    
    Supports three modes:
    1. 'polygon' - Use Polygon.io only
    2. 'yfinance' - Use yfinance only
    3. 'auto' - Try Polygon.io first, fallback to yfinance (RECOMMENDED)
    """
    
    @staticmethod
    def create_provider(
        provider_type: Optional[str] = None
    ) -> DataProviderInterface:
        """
        Create a data provider instance based on configuration.
        
        Args:
            provider_type: Override provider type ('polygon', 'yfinance', 'auto')
                          If None, uses settings.data_provider
        
        Returns:
            DataProviderInterface instance (may be FallbackDataProvider)
        """
        settings = get_settings()
        provider_type = provider_type or settings.data_provider
        
        logger.info(f"Creating data provider: {provider_type}")
        
        if provider_type == "polygon":
            # Polygon.io only
            if not settings.polygon_api_key:
                logger.error("Polygon.io selected but no API key found")
                raise ValueError(
                    "POLYGON_API_KEY not set in .env. "
                    "Either add the key or set DATA_PROVIDER=yfinance"
                )
            return PolygonProvider(api_key=settings.polygon_api_key)
        
        elif provider_type == "yfinance":
            # yfinance only
            logger.warning(
                "Using yfinance only - data quality may be lower than Polygon.io"
            )
            return YFinanceProvider()
        
        elif provider_type == "auto":
            # Auto mode: Try Polygon, fallback to yfinance
            try:
                if settings.polygon_api_key:
                    logger.info(
                        "Auto mode: Using Polygon.io (primary) with yfinance (fallback)"
                    )
                    primary = PolygonProvider(api_key=settings.polygon_api_key)
                    fallback = YFinanceProvider()
                    return FallbackDataProvider(primary, fallback)
                else:
                    logger.warning(
                        "Auto mode: No Polygon API key found, using yfinance only"
                    )
                    return YFinanceProvider()
            except Exception as e:
                logger.error(f"Error creating Polygon provider: {str(e)}")
                logger.info("Falling back to yfinance only")
                return YFinanceProvider()
        
        else:
            raise ValueError(
                f"Invalid DATA_PROVIDER: {provider_type}. "
                f"Must be 'polygon', 'yfinance', or 'auto'"
            )
    
    @staticmethod
    def create_options_provider(
        provider_type: Optional[str] = None
    ) -> DataProviderInterface:
        """
        Create a provider specifically for options data.
        
        Polygon's options support is incomplete (missing bid/ask/volume),
        so we use yfinance for options until Polygon implementation is complete.
        
        Args:
            provider_type: Override provider type
        
        Returns:
            DataProviderInterface instance suitable for options
        """
        # Use yfinance for options - Polygon doesn't have complete options data yet
        # TODO: Once Polygon options implementation is complete, use fallback strategy
        logger.info("Creating options provider: using yfinance (Polygon options incomplete)")
        return YFinanceProvider()


@lru_cache()
def get_data_provider() -> DataProviderInterface:
    """
    FastAPI dependency injection function.
    
    Returns cached data provider instance.
    Used in router endpoints as: provider: DataProviderInterface = Depends(get_data_provider)
    
    Example:
        @router.post("/analyze")
        async def analyze(
            request: Request,
            provider: DataProviderInterface = Depends(get_data_provider)
        ):
            data = await provider.get_historical_prices(...)
    """
    return ProviderFactory.create_provider()


@lru_cache()
def get_options_provider() -> DataProviderInterface:
    """
    FastAPI dependency injection function for options-specific provider.
    
    Returns cached options provider instance.
    """
    return ProviderFactory.create_options_provider()
