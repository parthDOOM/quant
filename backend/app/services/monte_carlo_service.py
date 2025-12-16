"""Monte Carlo simulation service using C++ engine."""
import sys
from pathlib import Path

# Add services directory to path for C++ module
services_dir = Path(__file__).parent
sys.path.insert(0, str(services_dir))

import numpy as np
from typing import List, Dict, Any

try:
    import core_cpp
    CPP_AVAILABLE = True
except ImportError:
    CPP_AVAILABLE = False
    print("WARNING: C++ module not available, Monte Carlo simulation will be disabled")


class MonteCarloService:
    """Service for running Monte Carlo simulations on portfolio paths."""
    
    @staticmethod
    def simulate_portfolio(
        tickers: List[str],
        initial_prices: List[float],
        expected_returns: List[float],
        covariance_matrix: List[List[float]],
        num_simulations: int = 1000,
        num_days: int = 252,
        portfolio_weights: List[float] = None
    ) -> Dict[str, Any]:
        """
        Run Monte Carlo simulation for portfolio.
        
        Args:
            tickers: List of ticker symbols
            initial_prices: Starting price for each asset
            expected_returns: Daily expected returns for each asset
            covariance_matrix: Covariance matrix (n x n)
            num_simulations: Number of simulation paths
            num_days: Number of days to simulate (default: 252 = 1 year)
            
        Returns:
            Dictionary containing:
                - simulations: Full 3D array of price paths
                - statistics: Summary statistics (percentiles, mean, std)
                - final_prices: Distribution of final prices
        """
        if not CPP_AVAILABLE:
            raise RuntimeError("C++ module not available. Cannot run Monte Carlo simulation.")
        
        # Initialize C++ simulator
        simulator = core_cpp.MonteCarloSimulator(num_simulations, num_days)
        
        # Run simulation
        simulations = simulator.simulate(
            expected_returns,
            covariance_matrix,
            initial_prices
        )
        
        # Convert to numpy for analysis
        sim_array = np.array(simulations)  # shape: (num_sims, num_days, num_assets)
        
        # Calculate portfolio values (using provided weights)
        if portfolio_weights is None:
            portfolio_weights = np.ones(len(tickers)) / len(tickers)
        else:
            portfolio_weights = np.array(portfolio_weights)
        portfolio_values = np.dot(sim_array, portfolio_weights)  # shape: (num_sims, num_days)
        
        # Extract final day values
        final_values = portfolio_values[:, -1]
        
        # Debug logging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Final values sample (first 10): {final_values[:10].tolist()}")
        logger.info(f"Final values stats: min={np.min(final_values)}, max={np.max(final_values)}, mean={np.mean(final_values)}")
        
        # Calculate statistics
        statistics = {
            "mean": float(np.mean(final_values)),
            "std": float(np.std(final_values)),
            "percentile_5": float(np.percentile(final_values, 5)),
            "percentile_25": float(np.percentile(final_values, 25)),
            "percentile_50": float(np.percentile(final_values, 50)),
            "percentile_75": float(np.percentile(final_values, 75)),
            "percentile_95": float(np.percentile(final_values, 95)),
            "min": float(np.min(final_values)),
            "max": float(np.max(final_values))
        }
        
        # Sanitize NaN/Inf values
        def sanitize_float(val):
            if np.isnan(val) or np.isinf(val):
                return 0.0
            return val
        
        statistics = {k: sanitize_float(v) for k, v in statistics.items()}
        
        # Calculate per-asset statistics
        asset_statistics = {}
        for i, ticker in enumerate(tickers):
            asset_final = sim_array[:, -1, i]
            asset_statistics[ticker] = {
                "mean": sanitize_float(float(np.mean(asset_final))),
                "std": sanitize_float(float(np.std(asset_final))),
                "percentile_5": sanitize_float(float(np.percentile(asset_final, 5))),
                "percentile_50": sanitize_float(float(np.percentile(asset_final, 50))),
                "percentile_95": sanitize_float(float(np.percentile(asset_final, 95)))
            }
        
        # Get sample paths for visualization (10 random paths)
        sample_indices = np.random.choice(num_simulations, size=min(10, num_simulations), replace=False)
        sample_paths = portfolio_values[sample_indices]
        
        # Sanitize all arrays for JSON compliance
        def sanitize_array(arr):
            """Replace NaN/Inf with 0.0 for JSON compliance."""
            arr = np.nan_to_num(arr, nan=0.0, posinf=0.0, neginf=0.0)
            return arr.tolist()
        
        return {
            "tickers": tickers,
            "num_simulations": num_simulations,
            "num_days": num_days,
            "portfolio_statistics": statistics,
            "asset_statistics": asset_statistics,
            "sample_paths": sanitize_array(sample_paths),
            "final_value_distribution": sanitize_array(final_values),
            "portfolio_weights": portfolio_weights.tolist() if isinstance(portfolio_weights, np.ndarray) else list(portfolio_weights)
        }
    
    @staticmethod
    def calculate_var_cvar(
        simulations: List[List[List[float]]],
        confidence_level: float = 0.95,
        initial_value: float = None
    ) -> Dict[str, float]:
        """
        Calculate Value at Risk (VaR) and Conditional VaR (CVaR).
        
        Args:
            simulations: 3D array from Monte Carlo
            confidence_level: Confidence level (e.g., 0.95 for 95%)
            initial_value: Initial portfolio value
            
        Returns:
            Dictionary with VaR and CVaR values
        """
        sim_array = np.array(simulations)
        
        # Calculate returns
        if initial_value is None:
            initial_value = np.sum(sim_array[0, 0, :])
        
        final_values = np.sum(sim_array[:, -1, :], axis=1)
        returns = (final_values - initial_value) / initial_value
        
        # Calculate VaR (percentile of losses)
        var_percentile = (1 - confidence_level) * 100
        var = float(np.percentile(returns, var_percentile))
        
        # Calculate CVaR (expected loss beyond VaR)
        losses_beyond_var = returns[returns <= var]
        cvar = float(np.mean(losses_beyond_var)) if len(losses_beyond_var) > 0 else var
        
        return {
            "var": var,
            "cvar": cvar,
            "confidence_level": confidence_level
        }
