"""
Unit tests for Options Data Service

Tests the fetching, cleaning, and processing of options chain data.
"""

import pytest
import pandas as pd
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from app.services.options_data import OptionsDataService


class TestOptionsDataService:
    """Test suite for OptionsDataService"""

    def test_calculate_time_to_expiry_valid_date(self):
        """Test time to expiry calculation with valid future date"""
        # Test with a date 90 days in the future
        future_date = (datetime.now() + timedelta(days=90)).strftime('%Y-%m-%d')
        tte = OptionsDataService._calculate_time_to_expiry(future_date)
        
        # Should be approximately 0.25 years (90/365)
        assert 0.24 < tte < 0.26
        assert isinstance(tte, float)

    def test_calculate_time_to_expiry_near_term(self):
        """Test time to expiry with very near-term expiration"""
        # Test with tomorrow's date
        tomorrow = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        tte = OptionsDataService._calculate_time_to_expiry(tomorrow)
        
        # Should be approximately 1/365
        assert 0 < tte < 0.01
        assert isinstance(tte, float)

    def test_calculate_time_to_expiry_past_date(self):
        """Test time to expiry with expired option (past date)"""
        # Test with yesterday's date
        yesterday = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
        tte = OptionsDataService._calculate_time_to_expiry(yesterday)
        
        # Should return minimum of 1 day (converted to years)
        assert tte > 0  # Should still be positive due to max(days, 1)

    def test_calculate_time_to_expiry_invalid_format(self):
        """Test time to expiry with invalid date format"""
        tte = OptionsDataService._calculate_time_to_expiry('invalid-date')
        
        # Should return 0.0 on error
        assert tte == 0.0

    def test_clean_options_data_filters_zero_bid(self):
        """Test that cleaning removes contracts with zero bid"""
        df = pd.DataFrame({
            'strike': [100, 105, 110],
            'bid': [0, 5.0, 6.0],
            'ask': [5.5, 6.0, 7.0],
            'volume': [100, 200, 300],
            'expiration': ['2025-11-15', '2025-11-15', '2025-11-15']
        })
        
        cleaned = OptionsDataService._clean_options_data(df, spot_price=105)
        
        # Should have 2 rows (zero bid removed)
        assert len(cleaned) == 2
        assert 100 not in cleaned['strike'].values

    def test_clean_options_data_filters_zero_volume(self):
        """Test that cleaning removes contracts with zero volume"""
        df = pd.DataFrame({
            'strike': [100, 105, 110],
            'bid': [5.0, 5.5, 6.0],
            'ask': [5.5, 6.0, 7.0],
            'volume': [0, 200, 300],
            'expiration': ['2025-11-15', '2025-11-15', '2025-11-15']
        })
        
        cleaned = OptionsDataService._clean_options_data(df, spot_price=105)
        
        # Should have 2 rows (zero volume removed)
        assert len(cleaned) == 2
        assert 100 not in cleaned['strike'].values

    def test_clean_options_data_calculates_mid_price(self):
        """Test that mid price is calculated correctly"""
        df = pd.DataFrame({
            'strike': [100, 105],
            'bid': [4.0, 5.0],
            'ask': [6.0, 7.0],
            'volume': [100, 200],
            'expiration': ['2025-11-15', '2025-11-15']
        })
        
        cleaned = OptionsDataService._clean_options_data(df, spot_price=105)
        
        # Mid price should be (bid + ask) / 2
        assert cleaned['mid_price'].iloc[0] == 5.0  # (4.0 + 6.0) / 2
        assert cleaned['mid_price'].iloc[1] == 6.0  # (5.0 + 7.0) / 2

    def test_clean_options_data_calculates_moneyness(self):
        """Test that moneyness is calculated correctly"""
        spot_price = 100.0
        df = pd.DataFrame({
            'strike': [90, 100, 110],
            'bid': [10.0, 5.0, 2.0],
            'ask': [11.0, 6.0, 3.0],
            'volume': [100, 200, 300],
            'expiration': ['2025-11-15', '2025-11-15', '2025-11-15']
        })
        
        cleaned = OptionsDataService._clean_options_data(df, spot_price=spot_price)
        
        # Moneyness should be strike / spot
        assert cleaned['moneyness'].iloc[0] == 0.90  # 90 / 100
        assert cleaned['moneyness'].iloc[1] == 1.00  # 100 / 100
        assert cleaned['moneyness'].iloc[2] == 1.10  # 110 / 100

    def test_clean_options_data_adds_time_to_expiry(self):
        """Test that time to expiry is added"""
        df = pd.DataFrame({
            'strike': [100],
            'bid': [5.0],
            'ask': [6.0],
            'volume': [100],
            'expiration': ['2025-11-15']
        })
        
        cleaned = OptionsDataService._clean_options_data(df, spot_price=105)
        
        # Should have time_to_expiry column
        assert 'time_to_expiry' in cleaned.columns
        assert cleaned['time_to_expiry'].iloc[0] > 0

    def test_clean_options_data_empty_dataframe(self):
        """Test cleaning with empty DataFrame"""
        df = pd.DataFrame()
        
        cleaned = OptionsDataService._clean_options_data(df, spot_price=100)
        
        # Should return empty DataFrame
        assert cleaned.empty

    @patch('app.services.options_data.yf.Ticker')
    def test_fetch_spot_price_success(self, mock_ticker):
        """Test successful spot price fetching"""
        # Mock the ticker object
        mock_hist = pd.DataFrame({
            'Close': [150.50]
        })
        mock_ticker_obj = Mock()
        mock_ticker_obj.history.return_value = mock_hist
        mock_ticker.return_value = mock_ticker_obj
        
        spot_price = OptionsDataService.fetch_spot_price('AAPL')
        
        assert spot_price == 150.50
        mock_ticker.assert_called_once_with('AAPL')
        mock_ticker_obj.history.assert_called_once_with(period='1d')

    @patch('app.services.options_data.yf.Ticker')
    def test_fetch_spot_price_no_data(self, mock_ticker):
        """Test spot price fetching with no data available"""
        # Mock empty history
        mock_ticker_obj = Mock()
        mock_ticker_obj.history.return_value = pd.DataFrame()
        mock_ticker.return_value = mock_ticker_obj
        
        with pytest.raises(ValueError, match="No price data available"):
            OptionsDataService.fetch_spot_price('INVALID')

    @patch('app.services.options_data.yf.Ticker')
    def test_fetch_spot_price_exception(self, mock_ticker):
        """Test spot price fetching with exception"""
        # Mock exception
        mock_ticker.side_effect = Exception("Network error")
        
        with pytest.raises(ValueError, match="Failed to fetch spot price"):
            OptionsDataService.fetch_spot_price('AAPL')

    @patch('app.services.options_data.OptionsDataService.fetch_spot_price')
    @patch('app.services.options_data.yf.Ticker')
    def test_fetch_options_chain_success(self, mock_ticker, mock_spot):
        """Test successful options chain fetching"""
        # Mock spot price
        mock_spot.return_value = 150.0
        
        # Mock options data
        mock_calls = pd.DataFrame({
            'strike': [145, 150, 155],
            'bid': [6.0, 3.0, 1.0],
            'ask': [7.0, 4.0, 2.0],
            'volume': [100, 200, 150],
            'lastPrice': [6.5, 3.5, 1.5],
            'impliedVolatility': [0.25, 0.23, 0.22]
        })
        
        mock_puts = pd.DataFrame({
            'strike': [145, 150, 155],
            'bid': [1.0, 3.0, 6.0],
            'ask': [2.0, 4.0, 7.0],
            'volume': [150, 250, 100],
            'lastPrice': [1.5, 3.5, 6.5],
            'impliedVolatility': [0.22, 0.23, 0.26]
        })
        
        mock_option_chain = Mock()
        mock_option_chain.calls = mock_calls
        mock_option_chain.puts = mock_puts
        
        mock_ticker_obj = Mock()
        mock_ticker_obj.options = ['2025-11-15', '2025-12-20']
        mock_ticker_obj.option_chain.return_value = mock_option_chain
        mock_ticker.return_value = mock_ticker_obj
        
        result = OptionsDataService.fetch_options_chain('AAPL')
        
        # Verify result structure
        assert result['ticker'] == 'AAPL'
        assert result['spot_price'] == 150.0
        assert result['risk_free_rate'] == OptionsDataService.DEFAULT_RISK_FREE_RATE
        assert len(result['expiration_dates']) == 2
        assert len(result['calls']) == 6  # 3 strikes × 2 expirations
        assert len(result['puts']) == 6

    @patch('app.services.options_data.yf.Ticker')
    def test_fetch_options_chain_no_options(self, mock_ticker):
        """Test options chain fetching with no options available"""
        # Mock ticker with no options
        mock_ticker_obj = Mock()
        mock_ticker_obj.options = []
        mock_ticker_obj.history.return_value = pd.DataFrame({'Close': [150.0]})
        mock_ticker.return_value = mock_ticker_obj
        
        with pytest.raises(ValueError, match="No options data available"):
            OptionsDataService.fetch_options_chain('STOCK')

    def test_get_options_summary(self):
        """Test options summary generation"""
        # Create mock options data
        calls_df = pd.DataFrame({
            'strike': [145, 150, 155],
            'volume': [100, 200, 150],
        })
        
        puts_df = pd.DataFrame({
            'strike': [145, 150, 155],
            'volume': [150, 250, 100],
        })
        
        options_data = {
            'ticker': 'AAPL',
            'spot_price': 150.0,
            'calls': calls_df,
            'puts': puts_df,
            'expiration_dates': ['2025-11-15', '2025-12-20']
        }
        
        summary = OptionsDataService.get_options_summary(options_data)
        
        assert summary['ticker'] == 'AAPL'
        assert summary['spot_price'] == 150.0
        assert summary['total_calls'] == 3
        assert summary['total_puts'] == 3
        assert summary['expiration_dates_count'] == 2
        assert summary['calls_strike_range']['min'] == 145
        assert summary['calls_strike_range']['max'] == 155
        assert summary['puts_strike_range']['min'] == 145
        assert summary['puts_strike_range']['max'] == 155

    def test_get_options_summary_empty_calls(self):
        """Test summary generation with empty calls DataFrame"""
        options_data = {
            'ticker': 'TEST',
            'spot_price': 100.0,
            'calls': pd.DataFrame(),
            'puts': pd.DataFrame({'strike': [95], 'volume': [100]}),
            'expiration_dates': ['2025-11-15']
        }
        
        summary = OptionsDataService.get_options_summary(options_data)
        
        assert summary['total_calls'] == 0
        assert summary['total_puts'] == 1
        assert 'calls_strike_range' not in summary
        assert 'puts_strike_range' in summary
