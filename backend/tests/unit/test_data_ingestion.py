"""
Unit tests for data ingestion service.
"""
import pytest
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

from app.services.data_ingestion import (
    fetch_and_process_prices,
    calculate_correlation_matrix,
    get_correlation_data,
    DataIngestionError,
    InsufficientDataError
)


@pytest.mark.unit
class TestDataIngestion:
    """Tests for data fetching and processing."""
    
    def test_fetch_and_process_prices_valid_tickers(self):
        """Test fetching data with valid tickers."""
        tickers = ["AAPL", "MSFT"]
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        
        returns = fetch_and_process_prices(tickers, start_date, end_date)
        
        # Assert returns is a DataFrame
        assert isinstance(returns, pd.DataFrame)
        
        # Assert we have data for both tickers
        assert len(returns.columns) >= 1  # At least one ticker should have data
        
        # Assert we have multiple rows
        assert len(returns) > 0
        
        # Assert all values are numeric
        assert returns.select_dtypes(include=[np.number]).shape == returns.shape
    
    def test_fetch_and_process_prices_single_ticker(self):
        """Test fetching data with a single ticker."""
        tickers = ["AAPL"]
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        
        # Should raise error because we need at least 2 tickers for correlation
        # But the function itself should work
        returns = fetch_and_process_prices(tickers, start_date, end_date)
        
        assert isinstance(returns, pd.DataFrame)
        assert "AAPL" in returns.columns
    
    def test_fetch_and_process_prices_invalid_ticker(self):
        """Test handling of invalid tickers."""
        tickers = ["INVALIDTICKER123", "AAPL"]
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        
        # Should still work if at least one ticker is valid
        returns = fetch_and_process_prices(tickers, start_date, end_date)
        
        assert isinstance(returns, pd.DataFrame)
        # AAPL should be present
        assert "AAPL" in returns.columns
    
    def test_fetch_and_process_prices_all_invalid(self):
        """Test with all invalid tickers."""
        tickers = ["INVALIDTICKER123", "ANOTHERBADTICKER"]
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        
        # Should raise InsufficientDataError
        with pytest.raises(InsufficientDataError):
            fetch_and_process_prices(tickers, start_date, end_date)


@pytest.mark.unit
class TestCorrelationMatrix:
    """Tests for correlation matrix calculation."""
    
    def test_calculate_correlation_matrix_valid_data(self):
        """Test correlation calculation with valid returns data."""
        # Create synthetic returns data
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        returns = pd.DataFrame({
            'Asset1': np.random.randn(100) * 0.02,
            'Asset2': np.random.randn(100) * 0.02,
            'Asset3': np.random.randn(100) * 0.02
        }, index=dates)
        
        corr_matrix = calculate_correlation_matrix(returns, min_periods=10)
        
        # Assert it's a DataFrame
        assert isinstance(corr_matrix, pd.DataFrame)
        
        # Assert it's square
        assert corr_matrix.shape[0] == corr_matrix.shape[1]
        
        # Assert diagonal is all 1.0 (correlation with itself)
        assert np.allclose(np.diag(corr_matrix.values), 1.0)
        
        # Assert it's symmetric
        assert np.allclose(corr_matrix.values, corr_matrix.values.T)
        
        # Assert all values are between -1 and 1
        assert (corr_matrix.values >= -1).all() and (corr_matrix.values <= 1).all()
    
    def test_calculate_correlation_matrix_perfect_correlation(self):
        """Test with perfectly correlated assets."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        base_returns = np.random.randn(100) * 0.02
        
        returns = pd.DataFrame({
            'Asset1': base_returns,
            'Asset2': base_returns,  # Identical to Asset1
        }, index=dates)
        
        corr_matrix = calculate_correlation_matrix(returns, min_periods=10)
        
        # Correlation between Asset1 and Asset2 should be 1.0
        assert np.isclose(corr_matrix.loc['Asset1', 'Asset2'], 1.0)
    
    def test_calculate_correlation_matrix_negative_correlation(self):
        """Test with negatively correlated assets."""
        dates = pd.date_range(start='2023-01-01', periods=100, freq='D')
        base_returns = np.random.randn(100) * 0.02
        
        returns = pd.DataFrame({
            'Asset1': base_returns,
            'Asset2': -base_returns,  # Opposite of Asset1
        }, index=dates)
        
        corr_matrix = calculate_correlation_matrix(returns, min_periods=10)
        
        # Correlation between Asset1 and Asset2 should be -1.0
        assert np.isclose(corr_matrix.loc['Asset1', 'Asset2'], -1.0)
    
    def test_calculate_correlation_matrix_insufficient_data(self):
        """Test with insufficient data points."""
        dates = pd.date_range(start='2023-01-01', periods=5, freq='D')
        returns = pd.DataFrame({
            'Asset1': np.random.randn(5) * 0.02,
            'Asset2': np.random.randn(5) * 0.02
        }, index=dates)
        
        # Require more data than available
        with pytest.raises(InsufficientDataError):
            calculate_correlation_matrix(returns, min_periods=10)


@pytest.mark.unit
class TestGetCorrelationData:
    """Tests for the high-level correlation data function."""
    
    def test_get_correlation_data_success(self):
        """Test successful end-to-end correlation data retrieval."""
        tickers = ["AAPL", "MSFT"]
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        
        returns, corr_matrix, metadata = get_correlation_data(
            tickers, start_date, end_date
        )
        
        # Assert returns
        assert isinstance(returns, pd.DataFrame)
        assert len(returns) > 0
        
        # Assert correlation matrix
        assert isinstance(corr_matrix, pd.DataFrame)
        assert corr_matrix.shape[0] == corr_matrix.shape[1]
        
        # Assert metadata
        assert 'actual_tickers' in metadata
        assert 'start_date' in metadata
        assert 'end_date' in metadata
        assert 'data_points' in metadata
        assert 'missing_tickers' in metadata
        
        # Assert data points matches returns length
        assert metadata['data_points'] == len(returns)
    
    def test_get_correlation_data_metadata_accuracy(self):
        """Test that metadata is accurate."""
        tickers = ["AAPL", "MSFT", "GOOGL"]
        start_date = "2023-06-01"
        end_date = "2023-06-30"
        
        returns, corr_matrix, metadata = get_correlation_data(
            tickers, start_date, end_date
        )
        
        # Tickers should be a list
        assert isinstance(metadata['actual_tickers'], list)
        
        # Should have at least 2 tickers
        assert len(metadata['actual_tickers']) >= 2
        
        # Data points should be positive
        assert metadata['data_points'] > 0
        
        # Dates should be strings in correct format
        assert isinstance(metadata['start_date'], str)
        assert isinstance(metadata['end_date'], str)
