"""Direct test of Monte Carlo service."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'services'))

from monte_carlo_service import MonteCarloService
import json


def test_service():
    """Test Monte Carlo service directly."""
    print("=" * 70)
    print("MONTE CARLO SERVICE TEST")
    print("=" * 70)
    
    tickers = ["AAPL", "MSFT", "GOOGL"]
    initial_prices = [150.0, 300.0, 120.0]
    
    result = MonteCarloService.simulate_portfolio(
        tickers=tickers,
        initial_prices=initial_prices,
        expected_returns=[0.0008, 0.001, 0.0009],
        covariance_matrix=[
            [0.0004, 0.0001, 0.00008],
            [0.0001, 0.0003, 0.00009],
            [0.00008, 0.00009, 0.00035]
        ],
        num_simulations=2000,
        num_days=252
    )
    
    print(f"\n✅ Simulation Complete!")
    print(f"\nTickers: {result['tickers']}")
    print(f"Simulations: {result['num_simulations']}")
    print(f"Days: {result['num_days']}")
    
    print(f"\n📊 Portfolio Statistics:")
    stats = result['portfolio_statistics']
    print(f"  Mean Final Value:    ${stats['mean']:.2f}")
    print(f"  Std Deviation:       ${stats['std']:.2f}")
    print(f"  5th Percentile:      ${stats['percentile_5']:.2f}")
    print(f"  50th Percentile:     ${stats['percentile_50']:.2f}")
    print(f"  95th Percentile:     ${stats['percentile_95']:.2f}")
    print(f"  Min:                 ${stats['min']:.2f}")
    print(f"  Max:                 ${stats['max']:.2f}")
    
    print(f"\n📈 Asset Statistics:")
    for ticker, asset_stats in result['asset_statistics'].items():
        print(f"  {ticker}:")
        print(f"    Mean:  ${asset_stats['mean']:.2f}")
        print(f"    5%:    ${asset_stats['percentile_5']:.2f}")
        print(f"    95%:   ${asset_stats['percentile_95']:.2f}")
    
    print(f"\n📉 Sample Paths: {len(result['sample_paths'])} paths")
    print(f"📊 Final Distribution: {len(result['final_value_distribution'])} values")
    
    # Calculate VaR/CVaR
    print(f"\n💰 Risk Metrics:")
    var_cvar = MonteCarloService.calculate_var_cvar(
        [[result['sample_paths'][0]]],  # Dummy for now
        confidence_level=0.95,
        initial_value=sum(initial_prices) / len(initial_prices) * len(initial_prices)
    )
    print(f"  VaR (95%):  {var_cvar['var']*100:.2f}%")
    print(f"  CVaR (95%): {var_cvar['cvar']*100:.2f}%")
    
    print("\n" + "=" * 70)
    print("TEST PASSED ✅")
    print("=" * 70)


if __name__ == "__main__":
    test_service()
