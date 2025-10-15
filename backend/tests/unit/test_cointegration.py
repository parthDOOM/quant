"""
Unit tests for Cointegration Service

Tests the core cointegration testing logic with synthetic and real data.
"""

import pytest
import pandas as pd
import numpy as np
from app.services.cointegration import CointegrationService


class TestCointegrationService:
    """Test suite for CointegrationService"""

    def test_cointegrated_synthetic_series(self):
        """Test that cointegration is detected between synthetic cointegrated series"""
        # Create cointegrated series: Y1 = random walk, Y2 = Y1 + noise
        np.random.seed(42)
        n = 100
        
        # Y1 is a random walk
        y1 = np.cumsum(np.random.randn(n))
        
        # Y2 is Y1 plus small noise (cointegrated relationship)
        y2 = y1 + np.random.randn(n) * 0.5
        
        series_a = pd.Series(y1, index=pd.date_range('2023-01-01', periods=n))
        series_b = pd.Series(y2, index=pd.date_range('2023-01-01', periods=n))
        
        result = CointegrationService.test_cointegration(series_a, series_b)
        
        assert result['p_value'] < 0.05, "Should detect cointegration (p < 0.05)"
        assert result['is_cointegrated'] == True
        assert 'hedge_ratio' in result
        assert 'half_life' in result
        assert 'correlation' in result
        assert result['hedge_ratio'] > 0, "Hedge ratio should be positive"

    def test_non_cointegrated_independent_walks(self):
        """Test that cointegration is NOT detected between independent random walks"""
        np.random.seed(42)
        n = 100
        
        # Two independent random walks
        y1 = np.cumsum(np.random.randn(n))
        y2 = np.cumsum(np.random.randn(n))
        
        series_a = pd.Series(y1, index=pd.date_range('2023-01-01', periods=n))
        series_b = pd.Series(y2, index=pd.date_range('2023-01-01', periods=n))
        
        result = CointegrationService.test_cointegration(series_a, series_b)
        
        # With independent walks, p-value should typically be high
        # Note: This can occasionally fail due to randomness, but probability is low
        assert result['p_value'] > 0.01, "Should NOT detect cointegration (p > 0.01)"
        assert result['is_cointegrated'] == False

    def test_hedge_ratio_calculation(self):
        """Test hedge ratio calculation with known linear relationship"""
        np.random.seed(42)
        n = 100
        
        # Create Y2 = 2 * Y1 + noise (hedge ratio should be close to 2)
        y1 = np.linspace(100, 200, n)
        y2 = 2 * y1 + np.random.randn(n) * 0.1
        
        series_a = pd.Series(y2, index=pd.date_range('2023-01-01', periods=n))
        series_b = pd.Series(y1, index=pd.date_range('2023-01-01', periods=n))
        
        hedge_ratio = CointegrationService._calculate_hedge_ratio(series_a, series_b)
        
        assert abs(hedge_ratio - 2.0) < 0.1, f"Hedge ratio should be ~2.0, got {hedge_ratio}"

    def test_spread_calculation(self):
        """Test spread calculation"""
        np.random.seed(42)
        n = 50
        
        y1 = pd.Series(np.random.randn(n) + 100, index=pd.date_range('2023-01-01', periods=n))
        y2 = pd.Series(np.random.randn(n) + 50, index=pd.date_range('2023-01-01', periods=n))
        hedge_ratio = 0.5
        
        spread = CointegrationService.calculate_spread(y1, y2, hedge_ratio)
        
        assert len(spread) == n
        assert isinstance(spread, pd.Series)
        # Check calculation: spread = y1 - hedge_ratio * y2
        expected_spread = y1 - hedge_ratio * y2
        pd.testing.assert_series_equal(spread, expected_spread)

    def test_zscore_calculation(self):
        """Test z-score calculation with rolling window"""
        np.random.seed(42)
        n = 100
        window = 20
        
        # Create a spread with known mean and std
        spread = pd.Series(np.random.randn(n) * 10 + 50, index=pd.date_range('2023-01-01', periods=n))
        
        zscore = CointegrationService.calculate_zscore(spread, window=window)
        
        assert len(zscore) == n
        assert isinstance(zscore, pd.Series)
        
        # First window-1 values should be NaN
        assert zscore.iloc[:window-1].isna().all()
        
        # Check that z-scores after window are calculated
        assert not zscore.iloc[window:].isna().all()

    def test_half_life_calculation(self):
        """Test half-life calculation for mean-reverting series"""
        np.random.seed(42)
        n = 200
        
        # Create mean-reverting AR(1) process with known lambda
        # X(t) = lambda * X(t-1) + epsilon
        lambda_true = 0.95
        x = np.zeros(n)
        x[0] = 0
        
        for t in range(1, n):
            x[t] = lambda_true * x[t-1] + np.random.randn() * 0.5
        
        spread = pd.Series(x, index=pd.date_range('2023-01-01', periods=n))
        
        half_life = CointegrationService._calculate_half_life(spread)
        
        # Theoretical half-life = -log(2) / log(lambda)
        theoretical_half_life = -np.log(2) / np.log(lambda_true)
        
        # Allow some tolerance due to estimation noise
        assert abs(half_life - theoretical_half_life) < 5, \
            f"Half-life {half_life} should be close to theoretical {theoretical_half_life}"

    def test_trading_signals_generation(self):
        """Test trading signal generation based on z-scores"""
        n = 100
        
        # Create z-score series with known patterns
        zscore = pd.Series(index=pd.date_range('2023-01-01', periods=n), dtype=float)
        zscore.iloc[0:20] = 0.5  # No signal (within threshold)
        zscore.iloc[20:30] = 2.5  # Short signal (z > 2)
        zscore.iloc[30:40] = -2.5  # Long signal (z < -2)
        zscore.iloc[40:50] = 0.1  # Exit signal (near 0)
        zscore.iloc[50:] = 1.0  # No signal
        
        signals = CointegrationService.generate_trading_signals(
            zscore,
            entry_threshold=2.0,
            exit_threshold=0.5
        )
        
        # Check short signals
        assert all(signals.iloc[20:30] == 'short'), "Should generate short signals when z > 2"
        
        # Check long signals
        assert all(signals.iloc[30:40] == 'long'), "Should generate long signals when z < -2"
        
        # Check exit signals
        assert all(signals.iloc[40:50] == 'exit'), "Should generate exit signals near 0"

    def test_insufficient_data_error(self):
        """Test that insufficient data raises ValueError"""
        n = 20  # Less than minimum 30
        series_a = pd.Series(np.random.randn(n), index=pd.date_range('2023-01-01', periods=n))
        series_b = pd.Series(np.random.randn(n), index=pd.date_range('2023-01-01', periods=n))
        
        with pytest.raises(ValueError, match="Insufficient data"):
            CointegrationService.test_cointegration(series_a, series_b)

    def test_all_nan_error(self):
        """Test that all NaN series raises ValueError"""
        n = 50
        series_a = pd.Series([np.nan] * n, index=pd.date_range('2023-01-01', periods=n))
        series_b = pd.Series(np.random.randn(n), index=pd.date_range('2023-01-01', periods=n))
        
        with pytest.raises(ValueError, match="all NaN"):
            CointegrationService.test_cointegration(series_a, series_b)

    def test_stationarity_test(self):
        """Test stationarity detection"""
        np.random.seed(42)
        n = 100
        
        # Stationary series (white noise)
        stationary_series = pd.Series(np.random.randn(n))
        p_value_stat, is_stationary_stat = CointegrationService.test_stationarity(stationary_series)
        
        # Should detect as stationary
        assert is_stationary_stat == True, "White noise should be stationary"
        assert p_value_stat < 0.05
        
        # Non-stationary series (random walk)
        non_stationary_series = pd.Series(np.cumsum(np.random.randn(n)))
        p_value_nonstat, is_stationary_nonstat = CointegrationService.test_stationarity(non_stationary_series)
        
        # Should detect as non-stationary
        assert is_stationary_nonstat == False, "Random walk should be non-stationary"
        assert p_value_nonstat > 0.05

    def test_result_structure(self):
        """Test that result dictionary contains all required fields"""
        np.random.seed(42)
        n = 100
        y1 = np.cumsum(np.random.randn(n))
        y2 = y1 + np.random.randn(n) * 0.5
        
        series_a = pd.Series(y1, index=pd.date_range('2023-01-01', periods=n))
        series_b = pd.Series(y2, index=pd.date_range('2023-01-01', periods=n))
        
        result = CointegrationService.test_cointegration(series_a, series_b)
        
        required_fields = [
            'p_value', 'test_statistic', 'is_cointegrated',
            'hedge_ratio', 'half_life', 'spread_mean', 'spread_std', 'correlation'
        ]
        
        for field in required_fields:
            assert field in result, f"Result should contain '{field}'"
            # Just check that value exists and is not None
            assert result[field] is not None, f"'{field}' should not be None"
