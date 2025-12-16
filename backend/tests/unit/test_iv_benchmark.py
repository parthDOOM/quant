"""Benchmark: C++ vs Python IV Calculator."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'app', 'services'))

import time
import numpy as np
from scipy.stats import norm
import core_cpp


# Python implementation (from implied_volatility.py)
def black_scholes_python(S, K, T, r, sigma, is_call, q=0.0):
    """Pure Python Black-Scholes."""
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    d2 = d1 - sigma * np.sqrt(T)
    
    if is_call:
        return S * np.exp(-q * T) * norm.cdf(d1) - K * np.exp(-r * T) * norm.cdf(d2)
    else:
        return K * np.exp(-r * T) * norm.cdf(-d2) - S * np.exp(-q * T) * norm.cdf(-d1)


def vega_python(S, K, T, r, sigma, q=0.0):
    """Pure Python Vega."""
    d1 = (np.log(S / K) + (r - q + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
    return S * np.exp(-q * T) * norm.pdf(d1) * np.sqrt(T)


def calculate_iv_python(market_price, S, K, T, r, is_call, q=0.0, max_iter=100, tol=1e-6):
    """Pure Python Newton-Raphson IV solver."""
    sigma = 0.25  # Initial guess
    
    for _ in range(max_iter):
        bs_price = black_scholes_python(S, K, T, r, sigma, is_call, q)
        price_diff = bs_price - market_price
        
        if abs(price_diff) < tol:
            return sigma
        
        vega_val = vega_python(S, K, T, r, sigma, q)
        
        if abs(vega_val) < 1e-8:
            return None
        
        sigma_new = sigma - price_diff / vega_val
        sigma_new = np.clip(sigma_new, 0.001, 5.0)
        
        if abs(sigma_new - sigma) < 1e-8:
            return None
        
        sigma = sigma_new
    
    return None


def run_benchmark():
    """Benchmark C++ vs Python IV calculation."""
    print("=" * 70)
    print("IMPLIED VOLATILITY BENCHMARK: C++ vs Python")
    print("=" * 70)
    
    calc = core_cpp.IVCalculator()
    
    # Test 1: Single option (warm-up)
    print("\n[Warm-up] Single option IV calculation")
    market_price = 12.36
    S, K, T, r = 100.0, 100.0, 1.0, 0.05
    
    iv_cpp = calc.calculate_iv(market_price, S, K, T, r, True)
    iv_py = calculate_iv_python(market_price, S, K, T, r, True)
    print(f"  C++ IV:    {iv_cpp:.6f}")
    print(f"  Python IV: {iv_py:.6f}")
    print(f"  Diff:      {abs(iv_cpp - iv_py):.8f}")
    
    # Test 2: Small batch (100 options)
    print("\n" + "-" * 70)
    print("Test 1: 100 options")
    print("-" * 70)
    
    n = 100
    market_prices = np.random.uniform(5, 20, n)
    spots = np.full(n, 100.0)
    strikes = np.random.uniform(80, 120, n)
    times = np.random.uniform(0.1, 2.0, n)
    rates = np.full(n, 0.05)
    is_calls = [bool(x) for x in np.random.randint(0, 2, n)]
    divs = np.zeros(n)
    
    # C++ batch
    start = time.time()
    ivs_cpp = calc.calculate_iv_batch(
        market_prices.tolist(),
        spots.tolist(),
        strikes.tolist(),
        times.tolist(),
        rates.tolist(),
        is_calls,
        divs.tolist()
    )
    time_cpp = time.time() - start
    
    # Python loop
    start = time.time()
    ivs_py = []
    for i in range(n):
        iv = calculate_iv_python(
            market_prices[i], spots[i], strikes[i],
            times[i], rates[i], is_calls[i]
        )
        ivs_py.append(iv if iv is not None else -1.0)
    time_py = time.time() - start
    
    speedup = time_py / max(time_cpp, 0.0001)  # Avoid division by zero
    print(f"  C++ Time:    {time_cpp:.4f}s")
    print(f"  Python Time: {time_py:.4f}s")
    print(f"  Speedup:     {speedup:.2f}x")
    
    # Test 3: Large batch (1000 options - typical options chain)
    print("\n" + "-" * 70)
    print("Test 2: 1000 options (realistic options chain)")
    print("-" * 70)
    
    n = 1000
    market_prices = np.random.uniform(0.5, 50, n)
    spots = np.random.uniform(80, 150, n)
    strikes = np.random.uniform(70, 160, n)
    times = np.random.uniform(0.05, 2.0, n)
    rates = np.random.uniform(0.03, 0.06, n)
    is_calls = [bool(x) for x in np.random.randint(0, 2, n)]
    divs = np.zeros(n)
    
    # C++ batch
    start = time.time()
    ivs_cpp = calc.calculate_iv_batch(
        market_prices.tolist(),
        spots.tolist(),
        strikes.tolist(),
        times.tolist(),
        rates.tolist(),
        is_calls,
        divs.tolist()
    )
    time_cpp = time.time() - start
    
    # Python loop
    start = time.time()
    ivs_py = []
    for i in range(n):
        iv = calculate_iv_python(
            market_prices[i], spots[i], strikes[i],
            times[i], rates[i], is_calls[i]
        )
        ivs_py.append(iv if iv is not None else -1.0)
    time_py = time.time() - start
    
    speedup = time_py / max(time_cpp, 1e-6)  # Avoid division by zero
    valid_cpp = sum(1 for iv in ivs_cpp if iv > 0)
    valid_py = sum(1 for iv in ivs_py if iv > 0)
    
    print(f"  C++ Time:      {time_cpp:.4f}s")
    print(f"  Python Time:   {time_py:.4f}s")
    print(f"  Speedup:       {speedup:.2f}x")
    print(f"  Valid C++:     {valid_cpp}/{n}")
    print(f"  Valid Python:  {valid_py}/{n}")
    
    if speedup > 15:
        print(f"  Status:        ✅ EXCELLENT ({speedup:.1f}x faster)")
    elif speedup > 10:
        print(f"  Status:        ✅ VERY GOOD ({speedup:.1f}x faster)")
    elif speedup > 5:
        print(f"  Status:        ✅ GOOD ({speedup:.1f}x faster)")
    else:
        print(f"  Status:        ⚠️  MODEST ({speedup:.1f}x faster)")
    
    # Test 4: Huge batch (5000 options)
    print("\n" + "-" * 70)
    print("Test 3: 5000 options (stress test)")
    print("-" * 70)
    
    n = 5000
    market_prices = np.random.uniform(0.5, 50, n)
    spots = np.random.uniform(80, 150, n)
    strikes = np.random.uniform(70, 160, n)
    times = np.random.uniform(0.05, 2.0, n)
    rates = np.random.uniform(0.03, 0.06, n)
    is_calls = [bool(x) for x in np.random.randint(0, 2, n)]
    divs = np.zeros(n)
    
    # C++ batch
    start = time.time()
    ivs_cpp = calc.calculate_iv_batch(
        market_prices.tolist(),
        spots.tolist(),
        strikes.tolist(),
        times.tolist(),
        rates.tolist(),
        is_calls,
        divs.tolist()
    )
    time_cpp = time.time() - start
    
    # Python loop  
    start = time.time()
    ivs_py = []
    for i in range(n):
        iv = calculate_iv_python(
            market_prices[i], spots[i], strikes[i],
            times[i], rates[i], is_calls[i]
        )
        ivs_py.append(iv if iv is not None else -1.0)
    time_py = time.time() - start
    
    speedup = time_py / max(time_cpp, 0.0001)  # Avoid division by zero
    print(f"  C++ Time:    {time_cpp:.4f}s")
    print(f"  Python Time: {time_py:.4f}s")
    print(f"  Speedup:     {speedup:.2f}x")
    
    print("\n" + "=" * 70)
    print("BENCHMARK COMPLETE")
    print("=" * 70)


if __name__ == "__main__":
    run_benchmark()
