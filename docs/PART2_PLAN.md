# Part 2: C++ Quantitative Engine - Implementation Plan

**Start Date:** October 17, 2025  
**Status:** Planning Phase  
**Approach:** Slow, methodical, test-driven

---

## Overview

Part 2 will integrate C++ with our Python backend to achieve 10-100x performance improvements on computationally intensive operations. We'll start with a simpler pilot project (Monte Carlo simulation) before tackling the more complex modules.

---

## Phase 1: Environment Setup & Prerequisites

### Prerequisites to Install:
1. **CMake** (3.15+) - Cross-platform build system
2. **C++ Compiler**
   - Windows: MSVC (Visual Studio Build Tools)
   - Linux/Mac: GCC or Clang
3. **Eigen** (3.3+) - C++ linear algebra library
4. **Pybind11** (2.10+) - Python/C++ bindings
5. **OpenMP** - Parallel programming (usually included with compiler)

### Installation Strategy:
- Install one at a time
- Verify each installation with a test
- Document any issues encountered
- Create test scripts to validate setup

---

## Phase 2: Build System Setup

### Directory Structure:
```
backend/
├── core/                           # NEW - C++ source code
│   ├── CMakeLists.txt             # Build configuration
│   ├── src/
│   │   └── monte_carlo.cpp        # Monte Carlo implementation
│   ├── include/
│   │   └── monte_carlo.h          # Header file
│   └── bindings/
│       └── python_bindings.cpp    # Pybind11 bindings
├── app/
│   └── services/
│       └── monte_carlo_service.py # Python wrapper (NEW)
└── tests/
    ├── unit/
    │   └── test_monte_carlo.py    # Python tests (NEW)
    └── cpp/                       # NEW - C++ unit tests
        └── test_monte_carlo.cpp
```

### Build Steps:
1. Create `CMakeLists.txt` with:
   - Project configuration
   - Pybind11 integration
   - Eigen dependency
   - OpenMP configuration
   - Python module output
2. Test build process
3. Verify Python can import C++ module

---

## Phase 3: Monte Carlo Pilot Project

### Why Monte Carlo First?
- **Simpler** than HRP/cointegration (good learning project)
- **Highly parallelizable** (showcases C++ benefits)
- **Independent** (doesn't affect existing modules)
- **Measurable** (easy to benchmark Python vs C++)

### Implementation Steps:

#### Step 1: C++ Core (monte_carlo.cpp)
```cpp
// Pseudocode structure
class MonteCarloSimulator {
public:
    MonteCarloSimulator(int num_simulations, int time_horizon);
    
    // Run simulation with portfolio weights and covariance
    std::vector<std::vector<double>> run_simulation(
        const Eigen::VectorXd& weights,
        const Eigen::MatrixXd& covariance,
        const Eigen::VectorXd& mean_returns,
        double initial_value
    );
    
private:
    int num_simulations_;
    int time_horizon_;
    
    // Cholesky decomposition for correlated random variables
    Eigen::MatrixXd cholesky_decomposition(const Eigen::MatrixXd& cov);
    
    // Parallel simulation loop with OpenMP
    void run_parallel_paths(/* params */);
};
```

#### Step 2: Python Bindings (python_bindings.cpp)
```cpp
// Pseudocode
PYBIND11_MODULE(quantlab_core, m) {
    py::class_<MonteCarloSimulator>(m, "MonteCarloSimulator")
        .def(py::init<int, int>())
        .def("run_simulation", &MonteCarloSimulator::run_simulation,
             "Run Monte Carlo simulation");
}
```

#### Step 3: Python Service (monte_carlo_service.py)
```python
# Pseudocode
import quantlab_core
import numpy as np
import pandas as pd

class MonteCarloService:
    def __init__(self):
        self.simulator = None
    
    async def run_simulation(
        self,
        tickers: List[str],
        weights: List[float],
        start_date: str,
        end_date: str,
        num_simulations: int = 10000,
        time_horizon: int = 252
    ):
        # 1. Fetch historical data
        prices = await fetch_prices(tickers, start_date, end_date)
        
        # 2. Calculate returns, mean, covariance
        returns = prices.pct_change()
        mean_returns = returns.mean()
        cov_matrix = returns.cov()
        
        # 3. Run C++ simulation
        simulator = quantlab_core.MonteCarloSimulator(
            num_simulations, time_horizon
        )
        paths = simulator.run_simulation(
            np.array(weights),
            cov_matrix.values,
            mean_returns.values,
            initial_value=100000
        )
        
        # 4. Calculate statistics
        final_values = [path[-1] for path in paths]
        percentiles = np.percentile(final_values, [5, 25, 50, 75, 95])
        
        return {
            "paths": paths,  # Sample of paths for visualization
            "statistics": {
                "mean": np.mean(final_values),
                "std": np.std(final_values),
                "percentiles": percentiles,
                "sharpe_ratio": calculate_sharpe(paths)
            }
        }
```

#### Step 4: API Endpoint
```python
# In backend/app/routers/monte_carlo.py
@router.post("/monte-carlo/simulate")
async def simulate_portfolio(
    request: MonteCarloRequest,
    service: MonteCarloService = Depends(get_monte_carlo_service)
):
    results = await service.run_simulation(
        tickers=request.tickers,
        weights=request.weights,
        start_date=request.start_date,
        end_date=request.end_date,
        num_simulations=request.num_simulations,
        time_horizon=request.time_horizon
    )
    return results
```

#### Step 5: Tests
```python
# backend/tests/unit/test_monte_carlo.py
import pytest
import quantlab_core
import numpy as np

def test_monte_carlo_import():
    """Test that C++ module can be imported"""
    assert hasattr(quantlab_core, 'MonteCarloSimulator')

def test_monte_carlo_basic_simulation():
    """Test basic simulation runs without error"""
    simulator = quantlab_core.MonteCarloSimulator(
        num_simulations=100,
        time_horizon=10
    )
    
    weights = np.array([0.5, 0.5])
    cov_matrix = np.array([[0.04, 0.01], [0.01, 0.09]])
    mean_returns = np.array([0.08, 0.12])
    
    paths = simulator.run_simulation(
        weights, cov_matrix, mean_returns, 100000
    )
    
    assert len(paths) == 100
    assert len(paths[0]) == 10

def test_monte_carlo_performance():
    """Benchmark C++ vs pure Python"""
    # Run same simulation in Python and C++
    # Assert C++ is at least 10x faster
    pass

@pytest.mark.integration
async def test_monte_carlo_endpoint(client):
    """Test full API endpoint"""
    response = await client.post(
        "/monte-carlo/simulate",
        json={
            "tickers": ["AAPL", "MSFT"],
            "weights": [0.5, 0.5],
            "start_date": "2023-01-01",
            "end_date": "2024-01-01",
            "num_simulations": 1000,
            "time_horizon": 252
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "paths" in data
    assert "statistics" in data
```

---

## Phase 4: Future Migrations (After Monte Carlo Success)

Once Monte Carlo is working, we can migrate existing Python modules to C++:

### 4.1: HRP Clustering Migration
- Correlation to distance transformation
- Hierarchical clustering (linkage)
- Matrix seriation
- **Expected speedup:** 5-20x

### 4.2: Cointegration Testing Migration
- OLS regression
- ADF test
- Half-life calculation
- **Expected speedup:** 3-10x

### 4.3: IV Surface Interpolation Migration
- Newton-Raphson solver
- Black-Scholes calculations
- Surface interpolation
- **Expected speedup:** 10-50x

---

## Testing Strategy

### For Each Component:
1. **Unit tests (C++)** - Test C++ functions in isolation
2. **Unit tests (Python)** - Test Python bindings work correctly
3. **Integration tests** - Test full API endpoint
4. **Performance tests** - Benchmark C++ vs Python
5. **Validation tests** - Ensure mathematical correctness

### Test Coverage Goals:
- C++ code: 80%+ coverage
- Python wrappers: 100% coverage
- API endpoints: 100% coverage

---

## Risk Mitigation

### Potential Issues:
1. **Build system complexity** - CMake can be tricky
   - Mitigation: Start simple, add complexity gradually
   
2. **Memory management** - C++/Python interface can leak
   - Mitigation: Use smart pointers, test for leaks
   
3. **Type conversions** - NumPy ↔ Eigen conversions
   - Mitigation: Use Pybind11's automatic conversion
   
4. **Platform compatibility** - Different OSes behave differently
   - Mitigation: Test on Windows first (your platform)
   
5. **Existing code breakage** - Don't break Part 1
   - Mitigation: Keep existing Python code, add C++ as option

---

## Success Criteria

### Phase 1 (Setup):
- ✅ CMake installed and working
- ✅ C++ compiler installed and working
- ✅ Eigen library available
- ✅ Pybind11 installed
- ✅ Can build simple "Hello World" C++ module
- ✅ Python can import C++ module

### Phase 2 (Build System):
- ✅ CMakeLists.txt compiles C++ to Python module
- ✅ Build process is documented
- ✅ Can rebuild after code changes

### Phase 3 (Monte Carlo):
- ✅ C++ Monte Carlo implementation working
- ✅ Python can call C++ Monte Carlo
- ✅ API endpoint returns correct results
- ✅ All tests passing
- ✅ C++ is 10x+ faster than Python
- ✅ Results match Python implementation

---

## Timeline Estimate

- **Phase 1 (Setup):** 1-2 hours
- **Phase 2 (Build System):** 2-3 hours
- **Phase 3 (Monte Carlo):** 4-6 hours
- **Total:** 7-11 hours

---

## Next Steps (Immediate)

1. ✅ Review this plan
2. ⏳ Check what's already installed on system
3. ⏳ Install CMake
4. ⏳ Install/verify C++ compiler
5. ⏳ Install Pybind11
6. ⏳ Install Eigen
7. ⏳ Create simple "Hello World" test
8. ⏳ Begin Monte Carlo implementation

---

**Ready to proceed?** Let's start with checking what's already installed!
