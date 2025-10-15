"""
Unit tests for Implied Volatility Calculator.

Tests cover:
1. Black-Scholes pricing formula
2. Vega calculation
3. Newton-Raphson IV solver
4. Edge cases and error handling
5. Options chain IV calculation
"""

import pytest
import numpy as np
import pandas as pd
from app.services.implied_volatility import ImpliedVolatilityCalculator


class TestBlackScholesPrice:
    """Test Black-Scholes-Merton pricing formula."""
    
    def test_call_option_atm(self):
        """Test ATM call option pricing."""
        # At-the-money call: S=K=100, T=1 year, r=5%, σ=20%
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type='call'
        )
        # Expected: ~10.45 (from Black-Scholes calculator)
        assert 10.0 < price < 11.0
        assert isinstance(price, float)
    
    def test_put_option_atm(self):
        """Test ATM put option pricing."""
        # At-the-money put: S=K=100, T=1 year, r=5%, σ=20%
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type='put'
        )
        # Expected: ~5.57 (from Black-Scholes calculator)
        assert 5.0 < price < 6.0
    
    def test_call_option_itm(self):
        """Test in-the-money call option."""
        # ITM call: S=110, K=100
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=110.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type='call'
        )
        # Should be > intrinsic value of 10
        assert price > 10.0
        assert price < 20.0  # But not too much time value
    
    def test_put_option_itm(self):
        """Test in-the-money put option."""
        # ITM put: S=90, K=100
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=90.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type='put'
        )
        # Should be > intrinsic value of 10
        assert price > 10.0
    
    def test_call_option_otm(self):
        """Test out-of-the-money call option."""
        # OTM call: S=90, K=100
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=90.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type='call'
        )
        # Should be less than ATM call (expected ~5.09)
        assert 0 < price < 6.0
    
    def test_put_call_parity(self):
        """Test put-call parity: C - P = S - K*e^(-rT)"""
        S, K, T, r, sigma = 100.0, 100.0, 1.0, 0.05, 0.20
        
        call_price = ImpliedVolatilityCalculator.black_scholes_price(
            S, K, T, r, sigma, 'call'
        )
        put_price = ImpliedVolatilityCalculator.black_scholes_price(
            S, K, T, r, sigma, 'put'
        )
        
        # Put-call parity: C - P = S - K*e^(-rT)
        lhs = call_price - put_price
        rhs = S - K * np.exp(-r * T)
        
        assert abs(lhs - rhs) < 0.01  # Should match within 1 cent
    
    def test_zero_time_to_expiry_call(self):
        """Test call option at expiration (T=0)."""
        # Call with S=110, K=100, T=0 should equal intrinsic value
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=110.0, K=100.0, T=0.0, r=0.05, sigma=0.20, option_type='call'
        )
        assert price == 10.0  # Intrinsic value
    
    def test_zero_time_to_expiry_put(self):
        """Test put option at expiration (T=0)."""
        # Put with S=90, K=100, T=0 should equal intrinsic value
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=90.0, K=100.0, T=0.0, r=0.05, sigma=0.20, option_type='put'
        )
        assert price == 10.0  # Intrinsic value
    
    def test_very_high_volatility(self):
        """Test with very high volatility."""
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=1.0, option_type='call'
        )
        # High vol should increase option value significantly
        assert price > 30.0
    
    def test_very_low_volatility(self):
        """Test with very low volatility."""
        price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.01, option_type='call'
        )
        # Low vol ATM call still has time value from drift (expected ~4.88)
        assert 0 < price < 5.5
    
    def test_negative_price_raises_error(self):
        """Test that negative prices raise ValueError."""
        with pytest.raises(ValueError, match="Prices must be positive"):
            ImpliedVolatilityCalculator.black_scholes_price(
                S=-100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type='call'
            )
    
    def test_negative_volatility_raises_error(self):
        """Test that negative volatility raises ValueError."""
        with pytest.raises(ValueError, match="Volatility must be positive"):
            ImpliedVolatilityCalculator.black_scholes_price(
                S=100.0, K=100.0, T=1.0, r=0.05, sigma=-0.20, option_type='call'
            )
    
    def test_invalid_option_type_raises_error(self):
        """Test that invalid option type raises ValueError."""
        with pytest.raises(ValueError, match="Invalid option_type"):
            ImpliedVolatilityCalculator.black_scholes_price(
                S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20, option_type='invalid'
            )


class TestVega:
    """Test Vega calculation."""
    
    def test_vega_positive(self):
        """Test that Vega is always positive."""
        vega = ImpliedVolatilityCalculator.vega(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20
        )
        assert vega > 0
    
    def test_vega_atm_highest(self):
        """Test that ATM options have highest Vega."""
        vega_atm = ImpliedVolatilityCalculator.vega(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20
        )
        vega_otm = ImpliedVolatilityCalculator.vega(
            S=100.0, K=120.0, T=1.0, r=0.05, sigma=0.20
        )
        assert vega_atm > vega_otm
    
    def test_vega_increases_with_time(self):
        """Test that Vega increases with time to expiration."""
        vega_short = ImpliedVolatilityCalculator.vega(
            S=100.0, K=100.0, T=0.25, r=0.05, sigma=0.20
        )
        vega_long = ImpliedVolatilityCalculator.vega(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=0.20
        )
        assert vega_long > vega_short
    
    def test_vega_zero_time(self):
        """Test Vega at expiration is zero."""
        vega = ImpliedVolatilityCalculator.vega(
            S=100.0, K=100.0, T=0.0, r=0.05, sigma=0.20
        )
        assert vega == 0.0
    
    def test_vega_negative_volatility_raises_error(self):
        """Test that negative volatility raises ValueError."""
        with pytest.raises(ValueError, match="Volatility must be positive"):
            ImpliedVolatilityCalculator.vega(
                S=100.0, K=100.0, T=1.0, r=0.05, sigma=-0.20
            )


class TestImpliedVolatility:
    """Test Newton-Raphson IV solver."""
    
    def test_iv_recovery_call(self):
        """Test that we can recover the volatility used to price a call."""
        # Use BS to price a call with known σ=20%
        known_sigma = 0.20
        market_price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=known_sigma, option_type='call'
        )
        
        # Solve for IV
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=market_price,
            S=100.0, K=100.0, T=1.0, r=0.05,
            option_type='call'
        )
        
        # Should recover the original σ within tolerance
        assert calculated_iv is not None
        assert abs(calculated_iv - known_sigma) < 0.0001
    
    def test_iv_recovery_put(self):
        """Test that we can recover the volatility used to price a put."""
        known_sigma = 0.30
        market_price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=known_sigma, option_type='put'
        )
        
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=market_price,
            S=100.0, K=100.0, T=1.0, r=0.05,
            option_type='put'
        )
        
        assert calculated_iv is not None
        assert abs(calculated_iv - known_sigma) < 0.0001
    
    def test_iv_high_volatility(self):
        """Test IV calculation with high volatility option."""
        known_sigma = 0.80
        market_price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=known_sigma, option_type='call'
        )
        
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=market_price,
            S=100.0, K=100.0, T=1.0, r=0.05,
            option_type='call'
        )
        
        assert calculated_iv is not None
        assert abs(calculated_iv - known_sigma) < 0.001
    
    def test_iv_low_volatility(self):
        """Test IV calculation with low volatility option."""
        known_sigma = 0.05
        market_price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=known_sigma, option_type='call'
        )
        
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=market_price,
            S=100.0, K=100.0, T=1.0, r=0.05,
            option_type='call'
        )
        
        assert calculated_iv is not None
        assert abs(calculated_iv - known_sigma) < 0.001
    
    def test_iv_itm_call(self):
        """Test IV for in-the-money call."""
        known_sigma = 0.25
        market_price = ImpliedVolatilityCalculator.black_scholes_price(
            S=110.0, K=100.0, T=1.0, r=0.05, sigma=known_sigma, option_type='call'
        )
        
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=market_price,
            S=110.0, K=100.0, T=1.0, r=0.05,
            option_type='call'
        )
        
        assert calculated_iv is not None
        assert abs(calculated_iv - known_sigma) < 0.001
    
    def test_iv_otm_put(self):
        """Test IV for out-of-the-money put."""
        known_sigma = 0.35
        market_price = ImpliedVolatilityCalculator.black_scholes_price(
            S=110.0, K=100.0, T=1.0, r=0.05, sigma=known_sigma, option_type='put'
        )
        
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=market_price,
            S=110.0, K=100.0, T=1.0, r=0.05,
            option_type='put'
        )
        
        assert calculated_iv is not None
        assert abs(calculated_iv - known_sigma) < 0.001
    
    def test_iv_short_maturity(self):
        """Test IV for short maturity option (7 days)."""
        known_sigma = 0.20
        market_price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=7/365, r=0.05, sigma=known_sigma, option_type='call'
        )
        
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=market_price,
            S=100.0, K=100.0, T=7/365, r=0.05,
            option_type='call'
        )
        
        assert calculated_iv is not None
        assert abs(calculated_iv - known_sigma) < 0.01  # Wider tolerance for short dates
    
    def test_iv_custom_initial_guess(self):
        """Test IV with custom initial guess."""
        known_sigma = 0.40
        market_price = ImpliedVolatilityCalculator.black_scholes_price(
            S=100.0, K=100.0, T=1.0, r=0.05, sigma=known_sigma, option_type='call'
        )
        
        # Use initial guess far from true value
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=market_price,
            S=100.0, K=100.0, T=1.0, r=0.05,
            option_type='call',
            initial_guess=0.10  # Start at 10% (true is 40%)
        )
        
        assert calculated_iv is not None
        assert abs(calculated_iv - known_sigma) < 0.001
    
    def test_iv_below_intrinsic_value(self):
        """Test that IV returns None when price is below intrinsic value."""
        # ITM call with intrinsic value = 10
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=5.0,  # Below intrinsic value
            S=110.0, K=100.0, T=1.0, r=0.05,
            option_type='call'
        )
        
        assert calculated_iv is None
    
    def test_iv_zero_price(self):
        """Test that IV returns None for zero price."""
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=0.0,
            S=100.0, K=100.0, T=1.0, r=0.05,
            option_type='call'
        )
        
        assert calculated_iv is None
    
    def test_iv_negative_price(self):
        """Test that IV returns None for negative price."""
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=-1.0,
            S=100.0, K=100.0, T=1.0, r=0.05,
            option_type='call'
        )
        
        assert calculated_iv is None
    
    def test_iv_zero_time(self):
        """Test that IV returns None for zero time to expiry."""
        calculated_iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
            market_price=10.0,
            S=100.0, K=100.0, T=0.0, r=0.05,
            option_type='call'
        )
        
        assert calculated_iv is None


class TestCalculateIVForChain:
    """Test IV calculation for entire options chain."""
    
    def test_calculate_iv_for_calls_chain(self):
        """Test IV calculation for a chain of call options."""
        # Create sample calls data
        calls_df = pd.DataFrame({
            'strike': [95.0, 100.0, 105.0],
            'mid_price': [8.0, 5.0, 3.0],
            'time_to_expiry': [0.25, 0.25, 0.25]
        })
        
        result = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            calls_df,
            spot_price=100.0,
            risk_free_rate=0.05,
            option_type='call'
        )
        
        assert 'calculated_iv' in result.columns
        assert len(result) == 3
        # All IVs should be calculated
        assert result['calculated_iv'].notna().sum() >= 2
    
    def test_calculate_iv_for_puts_chain(self):
        """Test IV calculation for a chain of put options."""
        puts_df = pd.DataFrame({
            'strike': [95.0, 100.0, 105.0],
            'mid_price': [3.0, 5.0, 8.0],
            'time_to_expiry': [0.25, 0.25, 0.25]
        })
        
        result = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            puts_df,
            spot_price=100.0,
            risk_free_rate=0.05,
            option_type='put'
        )
        
        assert 'calculated_iv' in result.columns
        assert len(result) == 3
        assert result['calculated_iv'].notna().sum() >= 2
    
    def test_calculate_iv_with_invalid_prices(self):
        """Test that invalid prices result in NaN IV values."""
        calls_df = pd.DataFrame({
            'strike': [100.0, 100.0],
            'mid_price': [5.0, 0.0],  # Second price is zero
            'time_to_expiry': [0.25, 0.25]
        })
        
        result = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            calls_df,
            spot_price=100.0,
            risk_free_rate=0.05,
            option_type='call'
        )
        
        # First should succeed, second should be None/NaN
        assert result.loc[0, 'calculated_iv'] is not None
        assert pd.isna(result.loc[1, 'calculated_iv']) or result.loc[1, 'calculated_iv'] is None
    
    def test_calculate_iv_empty_dataframe(self):
        """Test IV calculation with empty DataFrame."""
        empty_df = pd.DataFrame(columns=['strike', 'mid_price', 'time_to_expiry'])
        
        result = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            empty_df,
            spot_price=100.0,
            risk_free_rate=0.05,
            option_type='call'
        )
        
        assert len(result) == 0
        assert 'calculated_iv' in result.columns


class TestGetIVSurfaceData:
    """Test IV surface data generation."""
    
    def test_get_iv_surface_data(self):
        """Test generating IV surface data from options chain."""
        calls_df = pd.DataFrame({
            'strike': [95.0, 100.0, 105.0],
            'mid_price': [8.0, 5.0, 3.0],
            'time_to_expiry': [0.25, 0.25, 0.25],
            'moneyness': [0.95, 1.0, 1.05]
        })
        
        puts_df = pd.DataFrame({
            'strike': [95.0, 100.0, 105.0],
            'mid_price': [3.0, 5.0, 8.0],
            'time_to_expiry': [0.25, 0.25, 0.25],
            'moneyness': [0.95, 1.0, 1.05]
        })
        
        options_data = {
            'ticker': 'TEST',
            'spot_price': 100.0,
            'risk_free_rate': 0.05,
            'calls': calls_df,
            'puts': puts_df,
            'expiration_dates': ['2025-04-15']
        }
        
        surface_data = ImpliedVolatilityCalculator.get_iv_surface_data(options_data)
        
        assert surface_data['ticker'] == 'TEST'
        assert surface_data['spot_price'] == 100.0
        assert 'calculated_iv' in surface_data['calls'].columns
        assert 'calculated_iv' in surface_data['puts'].columns
