"""
Cointegration Testing Service

Implements Engle-Granger two-step cointegration test for identifying
mean-reverting pairs suitable for statistical arbitrage strategies.
"""

import pandas as pd
import numpy as np
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.regression.linear_model import OLS
from scipy import stats
from typing import Tuple, Dict, Optional
import logging

logger = logging.getLogger(__name__)


class CointegrationService:
    """Service for testing cointegration between asset pairs"""

    @staticmethod
    def test_cointegration(
        prices_a: pd.Series,
        prices_b: pd.Series,
        significance_level: float = 0.05
    ) -> Dict[str, float]:
        """
        Test for cointegration between two price series using Engle-Granger test.

        Args:
            prices_a: Price series for first asset
            prices_b: Price series for second asset
            significance_level: P-value threshold for cointegration (default: 0.05)

        Returns:
            Dictionary containing:
                - p_value: Engle-Granger test p-value
                - test_statistic: Test statistic value
                - is_cointegrated: Boolean indicating cointegration
                - hedge_ratio: Optimal hedge ratio from OLS regression
                - half_life: Mean reversion half-life in days
                - spread_mean: Mean of the spread
                - spread_std: Standard deviation of the spread
                - correlation: Pearson correlation coefficient

        Raises:
            ValueError: If series have insufficient data or are all NaN
        """
        # Validate inputs
        if len(prices_a) < 30 or len(prices_b) < 30:
            raise ValueError("Insufficient data: at least 30 observations required")

        if prices_a.isna().all() or prices_b.isna().all():
            raise ValueError("Price series cannot be all NaN values")

        # Align the series and drop NaN values
        df = pd.DataFrame({'a': prices_a, 'b': prices_b}).dropna()

        if len(df) < 30:
            raise ValueError("Insufficient overlapping data after removing NaN values")

        series_a = df['a']
        series_b = df['b']

        # Perform Engle-Granger cointegration test
        # This performs OLS regression and tests residuals for stationarity
        score, p_value, _ = coint(series_a, series_b)
        
        logger.info(f"Cointegration test: score={score:.4f}, p-value={p_value:.4f}, significance_level={significance_level}")

        # Calculate hedge ratio using OLS
        # Y = alpha + beta * X + epsilon
        # hedge_ratio = beta
        hedge_ratio = CointegrationService._calculate_hedge_ratio(series_a, series_b)
        logger.info(f"Calculated hedge_ratio={hedge_ratio:.4f}")

        # Calculate spread
        spread = series_a - hedge_ratio * series_b

        # Calculate half-life of mean reversion
        half_life = CointegrationService._calculate_half_life(spread)

        # Calculate spread statistics
        spread_mean = float(spread.mean())
        spread_std = float(spread.std())

        # Calculate correlation
        correlation = float(series_a.corr(series_b))

        # Determine if cointegrated based on p-value
        is_cointegrated = p_value < significance_level

        return {
            'p_value': float(p_value),
            'test_statistic': float(score),
            'is_cointegrated': is_cointegrated,
            'hedge_ratio': float(hedge_ratio),
            'half_life': float(half_life),
            'spread_mean': spread_mean,
            'spread_std': spread_std,
            'correlation': correlation
        }

    @staticmethod
    def _calculate_hedge_ratio(series_a: pd.Series, series_b: pd.Series) -> float:
        """
        Calculate optimal hedge ratio using OLS regression.

        Args:
            series_a: Dependent variable (Y)
            series_b: Independent variable (X)

        Returns:
            Beta coefficient (hedge ratio)
        """
        # Add constant term for OLS
        X = pd.DataFrame({'const': 1, 'b': series_b})
        model = OLS(series_a, X).fit()

        # Return the coefficient for series_b (beta)
        return model.params['b']

    @staticmethod
    def _calculate_half_life(spread: pd.Series) -> float:
        """
        Calculate mean reversion half-life using AR(1) model.

        The half-life is the expected time for the spread to mean-revert halfway
        back to its mean. Calculated from the AR(1) coefficient as:
        half_life = -log(2) / log(lambda)

        Args:
            spread: Spread time series

        Returns:
            Half-life in days (number of observations)
        """
        # Calculate lagged spread
        spread_lag = spread.shift(1)
        spread_ret = spread - spread_lag

        # Drop NaN from lag
        df = pd.DataFrame({'spread_lag': spread_lag, 'spread_ret': spread_ret}).dropna()

        if len(df) < 10:
            logger.warning("Insufficient data for half-life calculation, returning default")
            return 30.0  # Default to 30 days if insufficient data

        # Fit AR(1): spread(t) = mean + lambda * spread(t-1) + epsilon
        # Rearranged: spread_ret(t) = (lambda - 1) * spread(t-1) + epsilon
        X = df['spread_lag']
        y = df['spread_ret']

        # Simple linear regression
        model = OLS(y, X).fit()
        lambda_coef = model.params.iloc[0] + 1  # Add 1 because we used returns

        # Check if lambda is in valid range for mean reversion (0 < lambda < 1)
        if lambda_coef <= 0 or lambda_coef >= 1:
            logger.warning(f"Lambda coefficient {lambda_coef} outside valid range, using default")
            return 30.0

        # Calculate half-life
        half_life = -np.log(2) / np.log(lambda_coef)

        # Bound the half-life to reasonable values (1 to 252 trading days)
        half_life = max(1.0, min(half_life, 252.0))

        return half_life

    @staticmethod
    def calculate_spread(
        prices_a: pd.Series,
        prices_b: pd.Series,
        hedge_ratio: float
    ) -> pd.Series:
        """
        Calculate the spread between two price series.

        Args:
            prices_a: Price series for first asset
            prices_b: Price series for second asset
            hedge_ratio: Hedge ratio (beta from OLS regression)

        Returns:
            Spread time series
        """
        return prices_a - hedge_ratio * prices_b

    @staticmethod
    def calculate_zscore(
        spread: pd.Series,
        window: int = 20
    ) -> pd.Series:
        """
        Calculate rolling z-score of the spread.

        Args:
            spread: Spread time series
            window: Rolling window size for mean and std calculation

        Returns:
            Z-score time series
        """
        # Calculate rolling mean and std
        rolling_mean = spread.rolling(window=window, min_periods=window).mean()
        rolling_std = spread.rolling(window=window, min_periods=window).std()

        # Calculate z-score
        zscore = (spread - rolling_mean) / rolling_std

        return zscore

    @staticmethod
    def test_stationarity(series: pd.Series) -> Tuple[float, bool]:
        """
        Test if a time series is stationary using Augmented Dickey-Fuller test.

        Args:
            series: Time series to test

        Returns:
            Tuple of (p_value, is_stationary)
        """
        try:
            result = adfuller(series.dropna(), autolag='AIC')
            p_value = result[1]
            is_stationary = p_value < 0.05
            return p_value, is_stationary
        except Exception as e:
            logger.error(f"Error in stationarity test: {e}")
            return 1.0, False

    @staticmethod
    def generate_trading_signals(
        zscore: pd.Series,
        entry_threshold: float = 2.0,
        exit_threshold: float = 0.0
    ) -> pd.Series:
        """
        Generate trading signals based on z-score thresholds.

        Args:
            zscore: Z-score time series
            entry_threshold: Absolute z-score for entry (default: 2.0)
            exit_threshold: Absolute z-score for exit (default: 0.0)

        Returns:
            Series with signals: 'long', 'short', 'exit', or None
        """
        signals = pd.Series(index=zscore.index, dtype=object)

        # Entry signals
        signals[zscore > entry_threshold] = 'short'  # Spread too high, short it
        signals[zscore < -entry_threshold] = 'long'  # Spread too low, long it

        # Exit signals
        mask = (zscore.abs() <= exit_threshold) & (zscore.abs() > 0)
        signals[mask] = 'exit'

        return signals
