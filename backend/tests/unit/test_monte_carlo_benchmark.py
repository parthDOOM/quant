"""Test and benchmark Monte Carlo C++ vs Python implementation."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'services'))

import time
import numpy as np
import core_cpp


def monte_carlo_python(returns, cov_matrix, initial_prices, num_simulations, num_days):
    """Pure Python Monte Carlo implementation for comparison."""
    num_assets = len(returns)
    
    # Cholesky decomposition
    cov_np = np.array(cov_matrix)
    cholesky = np.linalg.cholesky(cov_np)
    
    # Initialize results
    results = np.zeros((num_simulations, num_days, num_assets))
    results[:, 0, :] = initial_prices
    
    # Run simulations
    for sim in range(num_simulations):
        for day in range(1, num_days):
            # Generate correlated randoms
            randoms = np.random.standard_normal(num_assets)
            correlated = cholesky @ randoms
            
            # Update prices (geometric Brownian motion)
            prev_prices = results[sim, day - 1, :]
            drift = np.array(returns)
            results[sim, day, :] = prev_prices * np.exp(drift + correlated)
    
    return results


def run_benchmark():
    """Run performance comparison between C++ and Python."""
    print("=" * 70)
    print("MONTE CARLO BENCHMARK: C++ vs Pure Python")
    print("=" * 70)
    
    # Test parameters
    test_cases = [
        (1000, 252, 2),   # 1000 sims, 1 year, 2 assets
        (5000, 252, 2),   # 5000 sims, 1 year, 2 assets
        (1000, 252, 5),   # 1000 sims, 1 year, 5 assets
    ]
    
    for num_sims, num_days, num_assets in test_cases:
        print(f"\nTest: {num_sims} simulations x {num_days} days x {num_assets} assets")
        print("-" * 70)
        
        # Generate test data
        returns = [0.001] * num_assets
        
        # Generate random positive definite covariance matrix
        A = np.random.rand(num_assets, num_assets)
        cov_matrix = (A @ A.T * 0.0001).tolist()
        
        initial_prices = [100.0] * num_assets
        
        # Test C++
        simulator = core_cpp.MonteCarloSimulator(num_sims, num_days)
        
        start = time.time()
        result_cpp = simulator.simulate(returns, cov_matrix, initial_prices)
        time_cpp = time.time() - start
        
        # Test Python
        start = time.time()
        result_python = monte_carlo_python(returns, cov_matrix, initial_prices, num_sims, num_days)
        time_python = time.time() - start
        
        # Calculate speedup
        speedup = time_python / time_cpp
        
        # Verify results are similar (check mean of final values)
        cpp_final = np.array(result_cpp)[:, -1, :]
        python_final = result_python[:, -1, :]
        
        cpp_mean = np.mean(cpp_final)
        python_mean = np.mean(python_final)
        diff_pct = abs(cpp_mean - python_mean) / python_mean * 100
        
        print(f"  C++ Time:        {time_cpp:.4f}s")
        print(f"  Python Time:     {time_python:.4f}s")
        print(f"  Speedup:         {speedup:.2f}x")
        print(f"  C++ Final Mean:  ${cpp_mean:.2f}")
        print(f"  Py Final Mean:   ${python_mean:.2f}")
        print(f"  Difference:      {diff_pct:.2f}%")
        
        if speedup > 5:
            print(f"  Status:          ✅ EXCELLENT ({speedup:.1f}x faster)")
        elif speedup > 2:
            print(f"  Status:          ✅ GOOD ({speedup:.1f}x faster)")
        else:
            print(f"  Status:          ⚠️  MODEST ({speedup:.1f}x faster)")
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


def test_correctness():
    """Test Monte Carlo implementation correctness."""
    print("\n" + "=" * 70)
    print("CORRECTNESS TESTS")
    print("=" * 70)
    
    # Test 1: Single asset, zero returns
    print("\nTest 1: Single asset, zero drift")
    mc = core_cpp.MonteCarloSimulator(100, 10)
    result = mc.simulate([0.0], [[0.0001]], [100.0])
    final_prices = [sim[-1][0] for sim in result]
    mean_final = np.mean(final_prices)
    print(f"  Initial: $100.00")
    print(f"  Final Mean: ${mean_final:.2f}")
    print(f"  ✅ Pass" if 95 < mean_final < 105 else "  ❌ Fail")
    
    # Test 2: Two assets, perfect correlation
    print("\nTest 2: Two assets, high correlation")
    mc = core_cpp.MonteCarloSimulator(1000, 50)
    cov = [[0.0004, 0.00038], [0.00038, 0.0004]]  # correlation ~0.95
    result = mc.simulate([0.001, 0.001], cov, [100.0, 100.0])
    
    # Extract final prices for both assets
    asset1_final = [sim[-1][0] for sim in result]
    asset2_final = [sim[-1][1] for sim in result]
    
    correlation = np.corrcoef(asset1_final, asset2_final)[0, 1]
    print(f"  Correlation: {correlation:.3f}")
    print(f"  ✅ Pass" if correlation > 0.8 else "  ❌ Fail")
    
    # Test 3: Positive drift should increase prices
    print("\nTest 3: Positive drift increases prices")
    mc = core_cpp.MonteCarloSimulator(1000, 252)
    result = mc.simulate([0.001], [[0.0001]], [100.0])
    final_prices = [sim[-1][0] for sim in result]
    mean_final = np.mean(final_prices)
    print(f"  Initial: $100.00")
    print(f"  Final Mean: ${mean_final:.2f}")
    print(f"  Expected: ~$127 (with 0.1% daily drift)")
    print(f"  ✅ Pass" if mean_final > 110 else "  ❌ Fail")
    
    print("\n" + "=" * 70)


if __name__ == "__main__":
    test_correctness()
    run_benchmark()
