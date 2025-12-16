"""Integration test for Monte Carlo API endpoint."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_monte_carlo_health():
    """Test health check endpoint."""
    response = client.get("/monte-carlo/health")
    assert response.status_code == 200
    data = response.json()
    print(f"Health check: {data}")
    assert data["status"] == "healthy"
    assert data["cpp_module"] == "loaded"


def test_monte_carlo_simulate():
    """Test Monte Carlo simulation endpoint."""
    request_data = {
        "tickers": ["AAPL", "MSFT"],
        "initial_prices": [150.0, 300.0],
        "expected_returns": [0.0008, 0.001],
        "covariance_matrix": [
            [0.0004, 0.0001],
            [0.0001, 0.0003]
        ],
        "num_simulations": 1000,
        "num_days": 252
    }
    
    response = client.post("/monte-carlo/simulate", json=request_data)
    assert response.status_code == 200
    
    data = response.json()
    
    # Validate response structure
    assert data["tickers"] == ["AAPL", "MSFT"]
    assert data["num_simulations"] == 1000
    assert data["num_days"] == 252
    
    # Check portfolio statistics
    stats = data["portfolio_statistics"]
    assert "mean" in stats
    assert "std" in stats
    assert "percentile_5" in stats
    assert "percentile_95" in stats
    
    # Check asset statistics
    assert "AAPL" in data["asset_statistics"]
    assert "MSFT" in data["asset_statistics"]
    
    # Check sample paths
    assert len(data["sample_paths"]) == 10  # 10 sample paths
    assert len(data["sample_paths"][0]) == 252  # 252 days per path
    
    # Check final value distribution
    assert len(data["final_value_distribution"]) == 1000
    
    print(f"\n✅ API Test Passed!")
    print(f"Portfolio Mean Final Value: ${stats['mean']:.2f}")
    print(f"Portfolio 5th Percentile: ${stats['percentile_5']:.2f}")
    print(f"Portfolio 95th Percentile: ${stats['percentile_95']:.2f}")
    print(f"AAPL Mean: ${data['asset_statistics']['AAPL']['mean']:.2f}")
    print(f"MSFT Mean: ${data['asset_statistics']['MSFT']['mean']:.2f}")


def test_monte_carlo_validation():
    """Test input validation."""
    # Test mismatched dimensions
    request_data = {
        "tickers": ["AAPL", "MSFT"],
        "initial_prices": [150.0],  # Wrong length
        "expected_returns": [0.0008, 0.001],
        "covariance_matrix": [[0.0004, 0.0001], [0.0001, 0.0003]],
        "num_simulations": 1000,
        "num_days": 252
    }
    
    response = client.post("/monte-carlo/simulate", json=request_data)
    assert response.status_code == 400
    print(f"✅ Validation test passed: {response.json()['detail']}")


if __name__ == "__main__":
    print("=" * 70)
    print("MONTE CARLO API INTEGRATION TESTS")
    print("=" * 70)
    
    test_monte_carlo_health()
    test_monte_carlo_simulate()
    test_monte_carlo_validation()
    
    print("\n" + "=" * 70)
    print("ALL TESTS PASSED ✅")
    print("=" * 70)
