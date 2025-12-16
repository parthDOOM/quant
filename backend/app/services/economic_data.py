"""
Economic Data Service

Fetches economic indicators from authoritative government sources.
Provides dynamic risk-free rate based on 3-Month Treasury Bill rates.
"""
import httpx
import logging
from datetime import datetime, timedelta
from typing import Optional
import asyncio

logger = logging.getLogger(__name__)

# U.S. Treasury FiscalData API endpoint for Treasury rates
TREASURY_API_URL = "https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v2/accounting/od/avg_interest_rates"

# Cache for risk-free rate (in-memory fallback)
_cached_rate: Optional[float] = None
_cache_timestamp: Optional[datetime] = None
_cache_ttl_hours = 12  # Cache for 12 hours


class EconomicDataError(Exception):
    """Base exception for economic data service errors."""
    pass


class EconomicDataService:
    """Service for fetching and caching economic indicators."""
    
    @staticmethod
    async def get_risk_free_rate(use_cache: bool = True) -> float:
        """
        Fetch the current risk-free rate (3-Month Treasury Bill rate).
        
        This function retrieves the latest 3-Month Treasury Bill Secondary Market Rate
        from the U.S. Department of the Treasury's FiscalData API. The rate is cached
        for 12 hours to minimize API calls.
        
        API Documentation:
        https://fiscaldata.treasury.gov/datasets/average-interest-rates-treasury-securities/
        
        Args:
            use_cache: Whether to use cached value if available (default: True)
            
        Returns:
            float: Risk-free rate as a decimal (e.g., 0.045 for 4.5%)
            
        Raises:
            EconomicDataError: If API request fails or data is invalid
        """
        global _cached_rate, _cache_timestamp
        
        # Check in-memory cache first
        if use_cache and _cached_rate is not None and _cache_timestamp is not None:
            age = datetime.now() - _cache_timestamp
            if age < timedelta(hours=_cache_ttl_hours):
                logger.info(
                    f"Using cached risk-free rate: {_cached_rate:.4f} "
                    f"(age: {age.seconds // 3600}h {(age.seconds % 3600) // 60}m)"
                )
                return _cached_rate
        
        # Fetch fresh data from Treasury API
        logger.info("Fetching risk-free rate from U.S. Treasury FiscalData API...")
        
        try:
            # Build query parameters
            # security_desc contains "Treasury Bills" for T-Bills
            # We want 3-Month Treasury Bills (security_type_desc = "Market Based")
            params = {
                "filter": "security_desc:eq:Treasury Bills",
                "sort": "-record_date",  # Most recent first
                "page[size]": "100",  # Get last 100 records
                "fields": "record_date,security_desc,security_type_desc,avg_interest_rate_amt"
            }
            
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(TREASURY_API_URL, params=params)
                response.raise_for_status()
                
                data = response.json()
                
                if "data" not in data or not data["data"]:
                    raise EconomicDataError("No data returned from Treasury API")
                
                # Find the most recent 3-Month T-Bill rate
                # Filter for "Market Based" type which includes 3-month bills
                records = data["data"]
                
                logger.debug(f"Received {len(records)} Treasury Bill records")
                
                # Look for the most recent record with a valid rate
                for record in records:
                    security_desc = record.get("security_desc", "")
                    rate_str = record.get("avg_interest_rate_amt")
                    record_date = record.get("record_date")
                    
                    if rate_str and "Treasury Bills" in security_desc:
                        try:
                            # Rate is provided as percentage (e.g., "4.50")
                            rate_pct = float(rate_str)
                            rate_decimal = rate_pct / 100.0
                            
                            # Cache the result
                            _cached_rate = rate_decimal
                            _cache_timestamp = datetime.now()
                            
                            logger.info(
                                f"✅ Fetched risk-free rate: {rate_pct:.2f}% ({rate_decimal:.6f}) "
                                f"from {record_date}"
                            )
                            
                            return rate_decimal
                            
                        except (ValueError, TypeError) as e:
                            logger.warning(f"Invalid rate value '{rate_str}': {e}")
                            continue
                
                # If we get here, no valid rate was found
                raise EconomicDataError(
                    "No valid 3-Month Treasury Bill rate found in API response"
                )
                
        except httpx.HTTPError as e:
            logger.error(f"HTTP error fetching risk-free rate: {e}")
            raise EconomicDataError(f"Failed to fetch risk-free rate: {e}")
            
        except Exception as e:
            logger.error(f"Unexpected error fetching risk-free rate: {e}", exc_info=True)
            raise EconomicDataError(f"Unexpected error: {e}")
    
    @staticmethod
    async def get_risk_free_rate_with_fallback(
        fallback_rate: float = 0.045
    ) -> float:
        """
        Get risk-free rate with fallback to default value on error.
        
        This is a safe wrapper around get_risk_free_rate() that returns
        a fallback rate if the API call fails, ensuring the application
        continues to function.
        
        Args:
            fallback_rate: Default rate to use if API fails (default: 4.5%)
            
        Returns:
            float: Risk-free rate as decimal, or fallback_rate on error
        """
        try:
            return await EconomicDataService.get_risk_free_rate()
        except Exception as e:
            logger.warning(
                f"Failed to fetch risk-free rate, using fallback {fallback_rate:.4f}: {e}"
            )
            return fallback_rate
    
    @staticmethod
    def clear_cache():
        """Clear the in-memory cache for risk-free rate."""
        global _cached_rate, _cache_timestamp
        _cached_rate = None
        _cache_timestamp = None
        logger.info("Cleared risk-free rate cache")


# Convenience function for backward compatibility
async def get_risk_free_rate() -> float:
    """
    Convenience function to get the risk-free rate.
    
    Returns:
        float: Risk-free rate as a decimal (e.g., 0.045 for 4.5%)
    """
    return await EconomicDataService.get_risk_free_rate_with_fallback()
