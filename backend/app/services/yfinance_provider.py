"""
YFinance Data Provider Implementation

Wrapper around existing yfinance logic implementing DataProviderInterface.
Serves as fallback provider when Polygon.io fails or for free-tier usage.

Note: yfinance is unofficial and may have reliability issues.
"""

import logging
from typing import Dict, List, Optional
import pandas as pd
import yfinance as yf

from app.services.provider_interface import DataProviderInterface, DataProviderError

logger = logging.getLogger(__name__)


class YFinanceProvider(DataProviderInterface):
    """
    YFinance API implementation of DataProviderInterface.
    
    Wraps existing yfinance logic from data_ingestion.py and options_data.py
    to provide consistent interface with Polygon.io provider.
    """
    
    def __init__(self):
        """Initialize yfinance provider (no API key required)"""
        logger.info(f"Initialized {self.name} provider")
    
    async def get_historical_prices(
        self,
        tickers: List[str],
        start_date: str,
        end_date: str,
        **kwargs
    ) -> pd.DataFrame:
        """
        Fetch historical adjusted closing prices using yfinance.
        
        This is the existing logic from data_ingestion.py adapted to async interface.
        
        Args:
            tickers: List of ticker symbols
            start_date: Start date (YYYY-MM-DD)
            end_date: End date (YYYY-MM-DD)
            **kwargs: Additional yfinance parameters
            
        Returns:
            DataFrame with adjusted closing prices (tickers as columns, dates as index)
        """
        try:
            logger.info(
                f"Fetching {len(tickers)} tickers from yfinance "
                f"({start_date} to {end_date})"
            )
            
            # Download data using yfinance
            data = yf.download(
                tickers=tickers,
                start=start_date,
                end=end_date,
                progress=False,
                threads=True,
                group_by='ticker',
                auto_adjust=False
            )
            
            if data.empty:
                raise DataProviderError(
                    "No data available for the specified tickers and date range"
                )
            
            # Extract prices (handle multi-level columns from yfinance 0.2.66+)
            prices = pd.DataFrame()
            
            if isinstance(data.columns, pd.MultiIndex):
                # Multi-level columns: (Ticker, Price) structure
                for ticker in tickers:
                    try:
                        if ticker in data.columns.get_level_values(0):
                            # Try Adj Close first
                            if (ticker, 'Adj Close') in data.columns:
                                ticker_data = data[(ticker, 'Adj Close')]
                            elif (ticker, 'Close') in data.columns:
                                ticker_data = data[(ticker, 'Close')]
                            else:
                                logger.warning(f"No price data for ticker: {ticker}")
                                continue
                            prices[ticker] = ticker_data
                        else:
                            logger.warning(f"No data available for ticker: {ticker}")
                    except (KeyError, AttributeError) as e:
                        logger.warning(f"Error extracting data for {ticker}: {str(e)}")
                        continue
            else:
                # Single-level columns
                if len(tickers) == 1:
                    if 'Adj Close' in data.columns:
                        prices = pd.DataFrame(data['Adj Close'])
                        prices.columns = [tickers[0]]
                    elif 'Close' in data.columns:
                        prices = pd.DataFrame(data['Close'])
                        prices.columns = [tickers[0]]
                    else:
                        raise DataProviderError(f"No price data found for ticker {tickers[0]}")
                else:
                    # Multi-ticker with single-level columns (shouldn't happen with current yfinance)
                    for ticker in tickers:
                        try:
                            if ticker in data.columns.get_level_values(0):
                                if 'Adj Close' in data[ticker].columns:
                                    ticker_data = data[ticker]['Adj Close']
                                elif 'Close' in data[ticker].columns:
                                    ticker_data = data[ticker]['Close']
                                else:
                                    logger.warning(f"No price data for ticker: {ticker}")
                                    continue
                                prices[ticker] = ticker_data
                            else:
                                logger.warning(f"No data available for ticker: {ticker}")
                        except (KeyError, AttributeError) as e:
                            logger.warning(f"Error extracting data for {ticker}: {str(e)}")
                            continue
            
            if prices.empty:
                raise DataProviderError(
                    "Failed to extract price data from yfinance response"
                )
            
            # Drop rows with all NaN values
            prices = prices.dropna(how='all')
            
            if len(prices) == 0:
                raise DataProviderError("Insufficient data after cleaning")
            
            logger.info(
                f"yfinance fetch complete: {len(prices)} days, "
                f"{len(prices.columns)} tickers"
            )
            
            return prices
            
        except Exception as e:
            logger.error(f"yfinance API error: {str(e)}")
            raise DataProviderError(f"yfinance fetch failed: {str(e)}")
    
    async def get_options_chain(
        self,
        ticker: str,
        expiration_date: Optional[str] = None,
        **kwargs
    ) -> Dict:
        """
        Fetch options chain using yfinance.
        
        This is the existing logic from options_data.py adapted to async interface.
        
        Args:
            ticker: Underlying ticker symbol
            expiration_date: Optional specific expiration (YYYY-MM-DD)
            **kwargs: Additional parameters
            
        Returns:
            Dictionary with options chain data
        """
        try:
            logger.info(f"Fetching options chain for {ticker} from yfinance")
            
            # Create ticker object
            ticker_obj = yf.Ticker(ticker)
            
            # Get spot price
            spot_price = await self.get_current_price(ticker)
            
            # Get available expiration dates
            expiration_dates = ticker_obj.options
            
            if not expiration_dates:
                raise DataProviderError(f"No options data available for ticker: {ticker}")
            
            logger.info(f"Found {len(expiration_dates)} expiration dates for {ticker}")
            
            # Fetch options data for each expiration date
            all_calls = []
            all_puts = []
            
            for exp_date in expiration_dates:
                # If specific expiration requested, filter
                if expiration_date and exp_date != expiration_date:
                    continue
                
                try:
                    opt_chain = ticker_obj.option_chain(exp_date)
                    
                    # Add expiration date to each row
                    if not opt_chain.calls.empty:
                        calls = opt_chain.calls.copy()
                        calls['expiration'] = exp_date
                        all_calls.append(calls)
                    
                    if not opt_chain.puts.empty:
                        puts = opt_chain.puts.copy()
                        puts['expiration'] = exp_date
                        all_puts.append(puts)
                        
                except Exception as e:
                    logger.warning(f"Error fetching options for {exp_date}: {str(e)}")
                    continue
            
            # Combine all expirations
            calls_df = pd.concat(all_calls, ignore_index=True) if all_calls else pd.DataFrame()
            puts_df = pd.concat(all_puts, ignore_index=True) if all_puts else pd.DataFrame()
            
            # Get risk-free rate (will be replaced by dynamic rate service)
            from app.services.options_data import OptionsDataService
            risk_free_rate = OptionsDataService.DEFAULT_RISK_FREE_RATE
            
            result = {
                'ticker': ticker,
                'spot_price': spot_price,
                'risk_free_rate': risk_free_rate,
                'calls': calls_df,
                'puts': puts_df,
                'expiration_dates': list(expiration_dates)
            }
            
            logger.info(
                f"Fetched {len(calls_df)} calls, {len(puts_df)} puts for {ticker}"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"yfinance options fetch error: {str(e)}")
            raise DataProviderError(f"Options fetch failed: {str(e)}")
    
    async def get_current_price(
        self,
        ticker: str,
        **kwargs
    ) -> float:
        """
        Fetch current price using yfinance.
        
        Args:
            ticker: Ticker symbol
            **kwargs: Additional parameters
            
        Returns:
            Current/latest closing price
        """
        try:
            ticker_obj = yf.Ticker(ticker)
            hist = ticker_obj.history(period='1d')
            
            if hist.empty:
                raise DataProviderError(f"No price data available for ticker: {ticker}")
            
            spot_price = float(hist['Close'].iloc[-1])
            logger.debug(f"Fetched current price for {ticker}: ${spot_price:.2f}")
            
            return spot_price
            
        except Exception as e:
            logger.error(f"Error fetching current price for {ticker}: {str(e)}")
            raise DataProviderError(f"Current price fetch failed: {str(e)}")
    
    @property
    def name(self) -> str:
        return "yfinance"
    
    @property
    def supports_options(self) -> bool:
        return True
    
    @property
    def supports_realtime(self) -> bool:
        return False
