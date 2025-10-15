"""
Implied Volatility Calculator using Black-Scholes-Merton model and Newton-Raphson solver.

This module provides functionality to:
1. Price options using the Black-Scholes-Merton formula
2. Calculate Vega (sensitivity to volatility changes)
3. Solve for implied volatility using Newton-Raphson method
4. Calculate IV for entire options chains

References:
- Black, F., & Scholes, M. (1973). The Pricing of Options and Corporate Liabilities
- Hull, J. (2018). Options, Futures, and Other Derivatives (10th ed.)
"""

import numpy as np
import pandas as pd
from scipy.stats import norm
from typing import Literal, Optional, Dict
import logging

logger = logging.getLogger(__name__)


class ImpliedVolatilityCalculator:
    """
    Calculator for implied volatility using Black-Scholes-Merton model.
    
    The Black-Scholes-Merton formula prices European options based on:
    - S: Spot price of the underlying asset
    - K: Strike price
    - T: Time to expiration (in years)
    - r: Risk-free interest rate
    - sigma: Volatility (standard deviation of returns)
    - q: Dividend yield (default 0 for simplicity)
    """
    
    # Constants for Newton-Raphson solver
    MAX_ITERATIONS = 100
    TOLERANCE = 1e-6  # Convergence tolerance (0.0001% in IV terms)
    MIN_VOLATILITY = 0.001  # 0.1% minimum volatility
    MAX_VOLATILITY = 5.0  # 500% maximum volatility
    INITIAL_GUESS = 0.25  # 25% starting volatility
    
    @staticmethod
    def _calculate_d1_d2(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float = 0.0
    ) -> tuple[float, float]:
        """
        Calculate d1 and d2 parameters for Black-Scholes formula.
        
        d1 = [ln(S/K) + (r - q + σ²/2)T] / (σ√T)
        d2 = d1 - σ√T
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            q: Dividend yield (default 0)
            
        Returns:
            Tuple of (d1, d2)
        """
        if T <= 0 or sigma <= 0:
            raise ValueError(f"Invalid parameters: T={T}, sigma={sigma}")
            
        sqrt_T = np.sqrt(T)
        d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * sqrt_T)
        d2 = d1 - sigma * sqrt_T
        
        return d1, d2
    
    @staticmethod
    def black_scholes_price(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        option_type: Literal['call', 'put'],
        q: float = 0.0
    ) -> float:
        """
        Calculate option price using Black-Scholes-Merton formula.
        
        Call price: C = S·e^(-qT)·N(d1) - K·e^(-rT)·N(d2)
        Put price:  P = K·e^(-rT)·N(-d2) - S·e^(-qT)·N(-d1)
        
        Where N(x) is the cumulative standard normal distribution.
        
        Args:
            S: Spot price of underlying
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free interest rate (annual)
            sigma: Volatility (annual standard deviation)
            option_type: 'call' or 'put'
            q: Dividend yield (default 0)
            
        Returns:
            Theoretical option price
            
        Raises:
            ValueError: If parameters are invalid
        """
        if S <= 0 or K <= 0:
            raise ValueError(f"Prices must be positive: S={S}, K={K}")
        if T <= 0:
            return max(0, S - K) if option_type == 'call' else max(0, K - S)
        if sigma <= 0:
            raise ValueError(f"Volatility must be positive: sigma={sigma}")
            
        try:
            d1, d2 = ImpliedVolatilityCalculator._calculate_d1_d2(S, K, T, r, sigma, q)
            
            if option_type == 'call':
                price = S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
            elif option_type == 'put':
                price = K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)
            else:
                raise ValueError(f"Invalid option_type: {option_type}. Must be 'call' or 'put'")
                
            return max(0, price)  # Price cannot be negative
            
        except Exception as e:
            logger.error(f"Error in black_scholes_price: {e}")
            raise
    
    @staticmethod
    def vega(
        S: float,
        K: float,
        T: float,
        r: float,
        sigma: float,
        q: float = 0.0
    ) -> float:
        """
        Calculate Vega: the sensitivity of option price to volatility changes.
        
        Vega = ∂Price/∂σ = S·e^(-qT)·φ(d1)·√T
        
        Where φ(x) is the standard normal probability density function.
        
        Vega is the same for both calls and puts (by put-call parity).
        
        Args:
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            sigma: Volatility
            q: Dividend yield (default 0)
            
        Returns:
            Vega value (sensitivity per 1.0 change in volatility)
        """
        if T <= 0:
            return 0.0
        if sigma <= 0:
            raise ValueError(f"Volatility must be positive: sigma={sigma}")
            
        try:
            d1, _ = ImpliedVolatilityCalculator._calculate_d1_d2(S, K, T, r, sigma, q)
            vega_value = S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)
            return vega_value
            
        except Exception as e:
            logger.error(f"Error in vega calculation: {e}")
            raise
    
    @staticmethod
    def calculate_implied_volatility(
        market_price: float,
        S: float,
        K: float,
        T: float,
        r: float,
        option_type: Literal['call', 'put'],
        q: float = 0.0,
        initial_guess: Optional[float] = None
    ) -> Optional[float]:
        """
        Calculate implied volatility using Newton-Raphson method.
        
        The algorithm iteratively solves:
        σ_new = σ_old - [BSM(σ_old) - market_price] / Vega(σ_old)
        
        Until |BSM(σ) - market_price| < tolerance or max iterations reached.
        
        Args:
            market_price: Observed market price of the option
            S: Spot price
            K: Strike price
            T: Time to expiration (years)
            r: Risk-free rate
            option_type: 'call' or 'put'
            q: Dividend yield (default 0)
            initial_guess: Starting volatility (default 25%)
            
        Returns:
            Implied volatility (as decimal, e.g., 0.25 = 25%) or None if no solution
        """
        # Input validation
        if market_price <= 0:
            logger.warning(f"Market price must be positive: {market_price}")
            return None
            
        if S <= 0 or K <= 0:
            logger.warning(f"Prices must be positive: S={S}, K={K}")
            return None
            
        if T <= 0:
            logger.warning(f"Time to expiration must be positive: T={T}")
            return None
        
        # Check intrinsic value constraint
        intrinsic_value = max(0, S - K) if option_type == 'call' else max(0, K - S)
        if market_price < intrinsic_value * 0.99:  # Allow 1% tolerance for bid-ask spread
            logger.warning(
                f"Market price {market_price:.4f} below intrinsic value {intrinsic_value:.4f}"
            )
            return None
        
        # Initialize
        sigma = initial_guess if initial_guess else ImpliedVolatilityCalculator.INITIAL_GUESS
        
        # Newton-Raphson iterations
        for iteration in range(ImpliedVolatilityCalculator.MAX_ITERATIONS):
            try:
                # Calculate option price with current volatility estimate
                bs_price = ImpliedVolatilityCalculator.black_scholes_price(
                    S, K, T, r, sigma, option_type, q
                )
                
                # Calculate price difference
                price_diff = bs_price - market_price
                
                # Check convergence
                if abs(price_diff) < ImpliedVolatilityCalculator.TOLERANCE:
                    # Ensure result is in valid range
                    if ImpliedVolatilityCalculator.MIN_VOLATILITY <= sigma <= ImpliedVolatilityCalculator.MAX_VOLATILITY:
                        return sigma
                    else:
                        logger.warning(f"Converged to out-of-range volatility: {sigma}")
                        return None
                
                # Calculate Vega for this volatility
                vega_value = ImpliedVolatilityCalculator.vega(S, K, T, r, sigma, q)
                
                # Avoid division by zero (Vega too small for deep ITM/OTM)
                if abs(vega_value) < 1e-8:
                    # Deep in/out-of-money options have negligible Vega
                    return None
                
                # Newton-Raphson update
                sigma_new = sigma - price_diff / vega_value
                
                # Enforce bounds
                sigma_new = np.clip(
                    sigma_new,
                    ImpliedVolatilityCalculator.MIN_VOLATILITY,
                    ImpliedVolatilityCalculator.MAX_VOLATILITY
                )
                
                # Check if we're making progress
                if abs(sigma_new - sigma) < 1e-8:
                    logger.warning(f"Stagnated at sigma={sigma:.6f}")
                    return None
                
                sigma = sigma_new
                
            except Exception as e:
                logger.error(f"Error in iteration {iteration}: {e}")
                return None
        
        # Max iterations reached
        logger.warning(
            f"Max iterations ({ImpliedVolatilityCalculator.MAX_ITERATIONS}) reached. "
            f"Last sigma={sigma:.4f}, price_diff={price_diff:.4f}"
        )
        return None
    
    @staticmethod
    def calculate_iv_for_chain(
        options_df: pd.DataFrame,
        spot_price: float,
        risk_free_rate: float,
        option_type: Literal['call', 'put']
    ) -> pd.DataFrame:
        """
        Calculate implied volatility for an entire options chain.
        
        Adds 'calculated_iv' column to the DataFrame with computed IV values.
        Options that fail to converge will have NaN in the IV column.
        
        Args:
            options_df: DataFrame with columns: strike, mid_price, time_to_expiry
            spot_price: Current price of underlying
            risk_free_rate: Annual risk-free rate
            option_type: 'call' or 'put'
            
        Returns:
            DataFrame with added 'calculated_iv' column
        """
        result_df = options_df.copy()
        calculated_ivs = []
        
        for idx, row in result_df.iterrows():
            try:
                iv = ImpliedVolatilityCalculator.calculate_implied_volatility(
                    market_price=row['mid_price'],
                    S=spot_price,
                    K=row['strike'],
                    T=row['time_to_expiry'],
                    r=risk_free_rate,
                    option_type=option_type
                )
                calculated_ivs.append(iv)
                
            except Exception as e:
                logger.error(f"Error calculating IV for row {idx}: {e}")
                calculated_ivs.append(None)
        
        result_df['calculated_iv'] = calculated_ivs
        
        # Log summary statistics
        valid_ivs = result_df['calculated_iv'].dropna()
        if len(valid_ivs) > 0:
            logger.info(
                f"Calculated IV for {len(valid_ivs)}/{len(result_df)} {option_type}s. "
                f"Mean IV: {valid_ivs.mean():.2%}, "
                f"Min: {valid_ivs.min():.2%}, "
                f"Max: {valid_ivs.max():.2%}"
            )
        else:
            logger.warning(f"No valid IVs calculated for {option_type}s")
        
        return result_df
    
    @staticmethod
    def get_iv_surface_data(options_data: Dict) -> Dict:
        """
        Calculate IV surface data suitable for 3D plotting.
        
        Args:
            options_data: Dictionary with 'calls', 'puts', 'spot_price', 'risk_free_rate'
            
        Returns:
            Dictionary with IV surface data for calls and puts
        """
        spot_price = options_data['spot_price']
        risk_free_rate = options_data['risk_free_rate']
        
        # Calculate IV for calls
        calls_with_iv = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            options_data['calls'],
            spot_price,
            risk_free_rate,
            'call'
        )
        
        # Calculate IV for puts
        puts_with_iv = ImpliedVolatilityCalculator.calculate_iv_for_chain(
            options_data['puts'],
            spot_price,
            risk_free_rate,
            'put'
        )
        
        return {
            'ticker': options_data['ticker'],
            'spot_price': spot_price,
            'risk_free_rate': risk_free_rate,
            'calls': calls_with_iv,
            'puts': puts_with_iv,
            'expiration_dates': options_data['expiration_dates']
        }
