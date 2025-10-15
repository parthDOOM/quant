"""
Validation tests against known financial data and relationships.
These tests verify the correctness of calculations using real market data.
"""
import pytest
import pandas as pd
import numpy as np

from app.services.data_ingestion import (
    fetch_and_process_prices,
    calculate_correlation_matrix,
    get_correlation_data
)


@pytest.mark.validation
@pytest.mark.slow
class TestCorrelationValidation:
    """Validation tests for correlation calculations using real market data."""
    
    def test_spy_voo_high_correlation(self):
        """
        Test that SPY and VOO (both S&P 500 ETFs) have very high correlation.
        These two ETFs track the same index and should be highly correlated (>0.99).
        """
        tickers = ["SPY", "VOO"]
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        returns, corr_matrix, metadata = get_correlation_data(
            tickers, start_date, end_date
        )
        
        # Both tickers should be present
        assert len(metadata['actual_tickers']) == 2
        
        # Correlation should be very high (>0.95)
        correlation = corr_matrix.iloc[0, 1]
        assert correlation > 0.95, f"SPY-VOO correlation ({correlation}) should be >0.95"
        
        print(f"\n✓ SPY-VOO correlation: {correlation:.4f} (Expected >0.95)")
    
    def test_tech_stocks_positive_correlation(self):
        """
        Test that major tech stocks (AAPL, MSFT, GOOGL) have positive correlations.
        Tech stocks typically move together due to sector dynamics.
        """
        tickers = ["AAPL", "MSFT", "GOOGL"]
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        returns, corr_matrix, metadata = get_correlation_data(
            tickers, start_date, end_date
        )
        
        # All pairs should have positive correlation
        for i in range(len(corr_matrix)):
            for j in range(i + 1, len(corr_matrix)):
                correlation = corr_matrix.iloc[i, j]
                ticker_i = corr_matrix.index[i]
                ticker_j = corr_matrix.columns[j]
                assert correlation > 0, (
                    f"{ticker_i}-{ticker_j} correlation ({correlation}) should be positive"
                )
                print(f"  {ticker_i}-{ticker_j}: {correlation:.4f}")
        
        print("\n✓ All tech stock pairs have positive correlation")
    
    def test_correlation_matrix_properties(self):
        """
        Test mathematical properties of correlation matrices.
        """
        tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]
        start_date = "2023-01-01"
        end_date = "2023-06-30"
        
        returns, corr_matrix, metadata = get_correlation_data(
            tickers, start_date, end_date
        )
        
        # Property 1: Diagonal should be 1.0 (correlation with self)
        diagonal = np.diag(corr_matrix.values)
        assert np.allclose(diagonal, 1.0), "Diagonal should be all 1.0"
        
        # Property 2: Matrix should be symmetric
        assert np.allclose(
            corr_matrix.values, corr_matrix.values.T
        ), "Correlation matrix should be symmetric"
        
        # Property 3: All values should be between -1 and 1
        assert (corr_matrix.values >= -1).all(), "All correlations should be >= -1"
        assert (corr_matrix.values <= 1).all(), "All correlations should be <= 1"
        
        # Property 4: Matrix should be positive semi-definite (all eigenvalues >= 0)
        eigenvalues = np.linalg.eigvals(corr_matrix.values)
        assert (eigenvalues >= -1e-10).all(), (
            f"Correlation matrix should be positive semi-definite. "
            f"Min eigenvalue: {eigenvalues.min()}"
        )
        
        print("\n✓ All correlation matrix mathematical properties validated")
        print(f"  - Diagonal: all 1.0 ✓")
        print(f"  - Symmetric: ✓")
        print(f"  - Range [-1, 1]: ✓")
        print(f"  - Positive semi-definite: ✓")
    
    def test_against_pandas_corr(self):
        """
        Validate our correlation calculation against pandas.DataFrame.corr().
        """
        tickers = ["AAPL", "MSFT", "GOOGL"]
        start_date = "2023-01-01"
        end_date = "2023-03-31"
        
        returns = fetch_and_process_prices(tickers, start_date, end_date)
        
        # Our implementation
        our_corr = calculate_correlation_matrix(returns)
        
        # Direct pandas calculation
        pandas_corr = returns.corr(method='pearson')
        
        # Should be nearly identical (within floating point tolerance)
        assert np.allclose(
            our_corr.values, pandas_corr.values, rtol=1e-10
        ), "Our correlation should match pandas.corr()"
        
        print("\n✓ Correlation calculation matches pandas.DataFrame.corr()")
    
    def test_sufficient_data_points(self):
        """
        Test that we get sufficient data points for meaningful correlation analysis.
        For monthly data over 1 year, we should get approximately 21 trading days per month.
        """
        tickers = ["AAPL", "MSFT"]
        start_date = "2023-01-01"
        end_date = "2023-12-31"
        
        returns, corr_matrix, metadata = get_correlation_data(
            tickers, start_date, end_date
        )
        
        # For a full year, expect around 252 trading days (minus holidays)
        assert metadata['data_points'] > 200, (
            f"Expected >200 trading days for full year, got {metadata['data_points']}"
        )
        
        print(f"\n✓ Sufficient data points: {metadata['data_points']} trading days")
    
    def test_date_range_accuracy(self):
        """
        Test that returned date ranges are within requested range.
        """
        tickers = ["AAPL", "MSFT"]
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        
        returns, corr_matrix, metadata = get_correlation_data(
            tickers, start_date, end_date
        )
        
        # Parse dates
        actual_start = pd.to_datetime(metadata['start_date'])
        actual_end = pd.to_datetime(metadata['end_date'])
        requested_start = pd.to_datetime(start_date)
        requested_end = pd.to_datetime(end_date)
        
        # Actual dates should be within or equal to requested range
        assert actual_start >= requested_start, "Start date should be >= requested"
        assert actual_end <= requested_end, "End date should be <= requested"
        
        print(f"\n✓ Date range validated:")
        print(f"  Requested: {start_date} to {end_date}")
        print(f"  Actual: {metadata['start_date']} to {metadata['end_date']}")


@pytest.mark.validation
class TestDataQuality:
    """Validation tests for data quality and handling."""
    
    def test_handles_mixed_valid_invalid_tickers(self):
        """
        Test that system handles mix of valid and invalid tickers gracefully.
        """
        tickers = ["AAPL", "INVALIDTICKER123", "MSFT", "BADTICKER999"]
        start_date = "2023-01-01"
        end_date = "2023-01-31"
        
        returns, corr_matrix, metadata = get_correlation_data(
            tickers, start_date, end_date
        )
        
        # Should have valid tickers
        assert len(metadata['actual_tickers']) >= 2
        
        # Should track missing tickers
        assert len(metadata['missing_tickers']) > 0
        
        # Valid tickers should be in actual_tickers
        assert "AAPL" in metadata['actual_tickers']
        assert "MSFT" in metadata['actual_tickers']
        
        print(f"\n✓ Successfully handled mixed tickers:")
        print(f"  Valid: {metadata['actual_tickers']}")
        print(f"  Missing: {metadata['missing_tickers']}")
