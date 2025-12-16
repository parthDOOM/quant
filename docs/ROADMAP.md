# **QuantLab Development Roadmap: Evolving to a High-Performance Platform**

## **Introduction: Strategic Evolution to a Hybrid C++/Python Architecture**

The initial QuantLab architecture represents a best-in-class approach for a research and analysis platform built with Python. However, to evolve into a truly institutional-grade system capable of high-fidelity simulations and low-latency strategy testing, it is essential to augment the Python orchestration layer with a high-performance C++ core.

This updated roadmap outlines a strategic, phased transition. We will first solidify the foundational data and infrastructure layers. Then, we will introduce a C++ quantitative engine as a pilot project to prove the integration architecture. Finally, we will leverage this new capability to build the platform's flagship feature: a high-fidelity, event-driven backtesting simulator. This hybrid approach will combine the rapid development and flexibility of Python with the raw computational power and low-level control of C++, creating a platform that is both powerful and maintainable.

---

## **Part 1: Foundational Infrastructure and Data Integrity**

**Objective:** To de-risk the platform by eliminating dependencies on unreliable data sources and implementing critical performance infrastructure. This phase is a non-negotiable prerequisite for any high-performance work.

### **1.1 Market Data Provider: A Comparative Technical Analysis**

Selecting a market data provider is a long-term architectural commitment that will define the platform's capabilities, reliability, and operational cost. The following analysis evaluates four leading providers against criteria critical to QuantLab's current modules (Hierarchical Risk Parity, Statistical Arbitrage, Implied Volatility Surface) and its future roadmap (live data, deeper risk analysis).

| Criterion | Alpha Vantage | Financial Modeling Prep (FMP) | Polygon.io | Finnhub |
| :---- | :---- | :---- | :---- | :---- |
| **Free Tier Limits** | 25 requests/day. Highly restrictive, unsuitable for sustained development or minimal application usage. | 250 calls/day. Serviceable for initial development and testing but insufficient for active use. | 5 API requests/minute. Allows for continuous, low-frequency development and basic application functionality. | 60 API calls/minute. The most generous free tier, robust enough for active development and light personal usage. |
| **Data Availability** | Equities, Forex, Crypto, Economic Indicators, and some Options data are available. The options data is not presented as a primary, institutional-grade product. | Equities, Forex, Crypto, Economic Data, and extensive Fundamental data. Explicitly does not provide real-time Options data. | Equities, **Institutional-grade Options**, Indices, Forex, Crypto. Options data is a core offering, sourced directly from the Options Price Reporting Authority (OPRA). | Equities, Forex, Crypto, Bonds, Economic Data, and extensive Fundamental data. Options data is not listed as a primary, supported offering. |
| **WebSocket Support** | No native WebSocket API is documented. Real-time functionality would require polling or integration with third-party services. | Yes, available for Stocks, Forex, and Crypto on paid subscription plans. | Yes, available for all asset classes on paid plans. The WebSocket API is well-documented and presented as a first-class feature for production systems. | Yes, available for Stocks, Forex, and Crypto. Notably, this is supported on the free tier for up to 50 symbols, a significant advantage. |
| **Python Client Library** | An official library, `alpha_vantage`, is available. It is functional but has received some community criticism regarding its JSON output structure. | Multiple third-party libraries exist (e.g., `fmp-py`, `py-fmpapi`), indicating community adoption but lacking a single, officially maintained standard. | Official, well-maintained client libraries are provided for multiple languages, including Python. Documentation strongly recommends their use for production environments. | An official Python library, `finnhub-python`, is available and documented as the primary method of interaction. |
| **Cost to Scale** | The first paid tier is **$49.99/month**, which provides 75 requests/minute. | The first paid tier is **$19/month** (billed annually), providing 300 calls/minute. This is a highly cost-effective entry point. | The first paid tier for real-time stocks or options data is **$199/month**. This reflects a higher quality of service and data, particularly for options. | Pricing is ambiguous for developers. The primary paid offering is an "All-In-One" enterprise plan at $3000/month. Other sources mention a $79.99/month plan, but the lack of clarity on the main pricing page is a risk. |

The analysis reveals that the platform's requirements for options data serve as a critical decision point. The existing Implied Volatility (IV) Surface module, and the planned high-priority Options "Greeks" module, are sophisticated features that are fundamentally dependent on the availability of accurate, complete, and low-latency options chain data. Any deficiency in this area would not merely degrade the feature but render it functionally useless and undermine the credibility of the entire platform.

### **1.2 Primary Recommendation and Strategic Justification**

**Primary Recommendation:** **Polygon.io**

**Justification:**
The selection of Polygon.io is a strategic investment in the quality, reliability, and future growth of QuantLab's most differentiating features. While other providers offer lower initial costs, they fail to meet the stringent data requirements of the platform's options analysis modules, making them a strategically unsound choice.

1.  **Unmatched Options Data Quality**: Polygon.io provides institutional-grade U.S. options market data sourced directly from the Options Price Reporting Authority (OPRA). This guarantees the highest level of accuracy and completeness, which is non-negotiable for the IV Surface and Greeks calculations. Migrating away from `yfinance` is an exercise in de-risking; selecting Polygon.io eliminates data quality risk for our most critical features.
2.  **Future-Proofing for Real-Time Capabilities**: The product roadmap includes a live price streaming dashboard and a high-fidelity backtester, features that demand a robust WebSocket API. Polygon.io's WebSocket service is a core, first-class component of their paid offering, engineered for high-performance, real-time applications.
3.  **Superior Developer Experience and Reliability**: Polygon.io invests in official, high-quality client libraries, including a well-maintained Python client. This reduces integration complexity, minimizes maintenance overhead, and ensures the integration is built upon a supported and documented foundation.
4.  **Strategic Acceptance of Cost**: The monthly cost for real-time data access ($199/month) is a core infrastructure investment, not an optional expense. The value of a credible, functional, and accurate options analysis suite far outweighs the marginal cost savings offered by providers with inferior data.

### **1.3 Backend Integration Blueprint**

The migration from `yfinance` to Polygon.io will be executed by refactoring the backend's data access layer to introduce a clean abstraction.

1.  **Establish a Data Provider Interface**: In the `backend/app/services/` directory, a new file `provider_interface.py` will define an abstract base class, `DataProviderInterface`, using Python's `abc` module. This class will declare the essential methods required by the application, such as `get_historical_prices(tickers, start, end)` and `get_options_chain(underlying_ticker, expiration_date)`.
2.  **Implement the Polygon.io Adapter**: A new module, `backend/app/services/polygon_provider.py`, will contain the `PolygonProvider` class, which inherits from `DataProviderInterface` and implements its methods using the official `polygon-python-client` library.
    * The `get_historical_prices` method will replace the `yfinance.download()` call currently in `backend/app/services/data_ingestion.py`. It will be implemented to call Polygon's Aggregates (Bars) API endpoint.
    * The `get_options_chain` method will replace the options-related `yfinance` calls in `backend/app/services/options_data.py`. This method will query Polygon's Options Contracts endpoint to fetch the complete chain of contracts for a given underlying symbol.
3.  **Refactor Existing Services with Dependency Injection**: The services in `data_ingestion.py` and `options_data.py` will be refactored to receive an instance of `DataProviderInterface` via FastAPI's dependency injection system. This decouples the services from the concrete implementation.
4.  **Configuration and Model Updates**: The Polygon.io API key will be managed as an environment variable and loaded via Pydantic's `BaseSettings`. Pydantic models in `backend/app/models/` will be updated to match the Polygon.io API response structures.

### **1.4 Dynamic Risk-Free Rate Implementation**

The hardcoded risk-free rate is a critical flaw. It must be replaced with a dynamic data feed.

* **Recommendation**: Utilize the official **U.S. Department of the Treasury's FiscalData API**.
* **Rationale**: Sourcing this data directly from the U.S. Treasury is architecturally superior to relying on a commercial provider, enhancing system resilience.
* **Implementation Plan**:
    1.  A new function, `get_risk_free_rate()`, will be created in `backend/app/services/economic_data.py`.
    2.  This function will make an HTTP GET request to the FiscalData API to fetch the latest 3-Month Treasury Bill rate.
    3.  The result will be parsed and converted to the required decimal format.
    4.  All services requiring this value will call the new function. The result will be aggressively cached with a TTL of several hours using the Redis layer.

---

## **Part 2: The C++ Quantitative Engine (Pilot Phase)**

**Objective:** To establish the C++/Python integration pipeline and deliver the first high-performance quantitative feature. This phase proves the architecture and provides a significant performance win.

### **2.1. C++/Python Integration and Build System Setup**

* **Action:** Integrate the **Pybind11** library and set up a **CMake** build system for the C++ components.
* **Justification:** Pybind11 is the industry standard for creating Python bindings for C++ code. CMake provides a robust, cross-platform build system for compiling the C++ code into a Python extension module that the FastAPI backend can import directly.
* **Implementation Steps:**
    1.  Create a new `core/` directory in the `backend/` for all C++ source code.
    2.  Set up a `CMakeLists.txt` file that handles the compilation of the C++ code and links against Pybind11 to produce a Python module (e.g., `quantlab_core.so` or `quantlab_core.pyd`).
    3.  Update the project's build process to automatically compile the C++ module during installation.

### **2.2. New Module: High-Performance Monte Carlo Engine (C++)**

* **Action:** Develop the core logic for the Monte Carlo simulation in C++ and expose it to the Python backend.
* **Justification:** This feature is computationally bound and highly parallelizable, making it a perfect pilot project for C++ integration. A C++ implementation will be orders of magnitude faster than a pure Python version.
* **Technical Implementation Plan:**
    * **Backend (C++):**
        * Create a `MonteCarloSimulator` class in C++.
        * The core simulation function will take portfolio weights, a covariance matrix, mean returns, and simulation parameters as input.
        * It will use a high-performance C++ linear algebra library (like **Eigen**) for the Cholesky decomposition.
        * The simulation loop will be parallelized using **OpenMP** to leverage multiple CPU cores.
        * Use Pybind11 to create Python bindings for this class, handling the conversion between NumPy arrays and Eigen matrices.
    * **Backend (Python):**
        * A new service, `simulation_service.py`, will import the compiled C++ module.
        * It will first use `pandas`/`numpy` to calculate the mean returns and covariance matrix from historical data.
        * It will then pass these inputs to the C++ Monte Carlo engine and receive the simulation results.
        * A new FastAPI endpoint, `/simulations/monte-carlo`, will expose this functionality.
    * **Frontend:**
        * A new page, `MonteCarloSimulation.tsx`, will provide a UI for users to input portfolio and simulation parameters.
        * Results will be visualized using a "fan chart" and a histogram in Plotly.js to show the range of potential outcomes and the final value distribution.

---

## **Part 3: High-Fidelity Backtesting and Feature Expansion**

**Objective:** To build the platform's flagship feature—a high-performance, event-driven backtesting simulator—and enhance existing modules with deeper analytics.

### **3.1. New Module: Event-Driven Backtesting Simulator (C++)**

* **Action:** Design and build a high-fidelity, event-driven backtesting engine in C++, inspired by the architecture of `orderbook-simulator-cpp`.
* **Justification:** This will be the core proprietary technology of QuantLab, enabling the testing of latency-sensitive and intraday strategies that are impossible to simulate with standard Python libraries.
* **Technical Implementation Plan:**
    * **Backend (C++):** This will be a major undertaking, broken into several components within the `core/` directory:
        * **Event System:** A queue-based event loop (`MarketEvent`, `SignalEvent`, `OrderEvent`, `FillEvent`).
        * **Data Handler:** A component for reading historical tick-by-tick or Level 2 order book data from files and generating `MarketEvent`s.
        * **Execution Handler:** A simulated matching engine that processes `OrderEvent`s, maintains an order book, and generates `FillEvent`s, accounting for slippage and transaction costs.
        * **Portfolio Manager:** A class that manages portfolio state, positions, and equity based on `FillEvent`s.
        * **Strategy Interface:** An abstract base class for user strategies to inherit from.
        * **Pybind11 Bindings:** Expose the backtesting engine to Python, allowing a user to pass in a Python-defined strategy class and backtest parameters.
    * **Backend (Python):** The `backtesting_service.py` will be the orchestration layer, providing an API to manage strategies and run backtests via the C++ engine.
    * **Frontend:** A new "Backtester" section in the UI will allow users to manage strategies, select data, and launch backtests, with a detailed results page showing an interactive equity curve and a full suite of performance metrics.

### **3.2. Other New Features and Enhancements (Reprioritized)**

* **Options "Greeks" Calculation (Priority: High)**
    * **Justification**: This feature is an essential and logical extension of the IV Surface module, providing the fundamental risk metrics required for any serious options analysis.
    * **Technical Implementation Plan**:
        * **Backend**:
            * **Library Integration**: The `py_vollib` library will be integrated into the backend. It is a well-regarded, pure Python library for options pricing and Greeks calculation.
            * **Service Modification**: Within `backend/app/services/options_data.py`, new functions will be created: `calculate_greeks_for_option(option_params)` and `calculate_greeks_surface(options_chain)`.
            * **Core Logic**: These functions will iterate through each option contract, invoking the analytical Greek calculation functions from `py_vollib`. All necessary inputs are already available from the existing IV Surface logic.
            * **API Endpoint**: A new API endpoint, `/options/greeks`, will be created.
        * **Frontend**:
            * **Greeks Data Table**: A new, sortable, and filterable table component will be built to display the calculated Greeks for every option contract.
            * **Interactive 3D Surfaces**: The existing 3D Plotly.js chart will be extended with UI controls to dynamically change the Z-axis of the plot from Implied Volatility to Delta, Gamma, Vega, or Theta.
        * **Data Requirements**: This feature depends on the full options chain data from Polygon.io.

* **HRP Portfolio Backtesting (Python Version) (Priority: Medium)**
    * **Justification**: This provides a simpler, daily-resolution backtester for portfolio-level strategies, serving as a valuable counterpart to the complex C++ engine.
    * **Technical Implementation Plan**:
        * **Backend**:
            * A new service, `backend/app/services/backtesting_service.py`, will be established.
            * The core function `run_hrp_backtest(...)` will execute a walk-forward backtest, rebalancing at a specified frequency.
            * At each rebalancing point, it will fetch historical data for a lookback period, compute HRP weights, and calculate realized returns for the next period.
            * It will compound returns to generate an equity curve and compute summary performance metrics (Sharpe Ratio, Max Drawdown).
        * **Frontend**:
            * A new React component, `HRPBacktestResults.tsx`, will visualize the backtest output with KPIs and an interactive equity curve chart comparing the strategy against a benchmark.
        * **Data Requirements**: Utilizes historical equity price data already provisioned.

* **Live Price Streaming & Dashboard (Priority: Medium)**
    * **Justification**: This feature transforms QuantLab into a dynamic market monitoring platform.
    * **Technical Implementation Plan**:
        * **Backend**:
            * A new router, `backend/app/routers/streaming.py`, will manage WebSocket connections using FastAPI's native support.
            * A `ConnectionManager` class will handle the lifecycle of client connections and ticker subscriptions.
            * The backend will establish its own WebSocket connection to the data provider (e.g., Finnhub's free tier for development, Polygon.io for production) and broadcast updates to subscribed clients.
        * **Frontend**:
            * A new page, `LiveDashboard.tsx`, will be created.
            * The `react-use-websocket` library will be used to manage the WebSocket connection.
            * Reusable components like `PriceTicker.tsx` will be developed to display real-time updates with visual cues for price changes.
        * **Data Requirements**: Requires a data provider with a WebSocket API.

* **Factor Analysis Module (Fama-French 3-Factor Model) (Priority: Low)**
    * **Justification**: This module introduces a classic, academically rigorous model for portfolio analysis.
    * **Technical Implementation Plan**:
        * **Backend**:
            * **Data Sourcing**: A utility script will be created to periodically download and parse the Fama-French factor data files from the Kenneth French Data Library.
            * **New Service**: A new service, `backend/app/services/factor_analysis_service.py`, will perform the analysis.
            * **Core Logic**: A function `run_fama_french_regression(...)` will use `statsmodels.api.OLS` to perform a multiple linear regression of an asset's excess returns against the three factors.
            * **API Endpoint**: A new endpoint, `/analysis/fama-french`, will be exposed.
        * **Frontend**:
            * A new page, `FactorAnalysis.tsx`, will allow users to select a stock and date range.
            * Results will be displayed in a table with interpretations for each metric.
        * **Data Requirements**: Requires a new, external data source: the Fama-French Data Library.

---

## **Part 4: Core Architecture and Quality-of-Life Improvements**

This section addresses critical non-functional requirements. Implementing these improvements will elevate QuantLab from a functional prototype to a performant, reliable, and deployable application.

### **4.1. Backend Caching**

* **Problem**: The absence of a caching layer leads to redundant, slow API calls to the data provider for identical requests.
* **Recommendation**: Implement a server-side caching layer using **Redis** and the `fastapi-cache2` library.
* **Action Plan**:
    1.  Add `redis` and `fastapi-cache2` to `requirements.txt`.
    2.  In `backend/app/main.py`, initialize the cache during the application's `lifespan` event.
        ```python
        # In backend/app/main.py
        from contextlib import asynccontextmanager
        from fastapi import FastAPI
        from fastapi_cache import FastAPICache
        from fastapi_cache.backends.redis import RedisBackend
        from redis import asyncio as aioredis
        import os

        @asynccontextmanager
        async def lifespan(app: FastAPI):
            redis_url = os.environ.get("REDIS_URL", "redis://localhost")
            redis = aioredis.from_url(redis_url)
            FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")
            yield
        ```
    3.  Apply the `@cache` decorator to expensive endpoints like `/hrp/analyze` with an appropriate TTL.
        ```python
        # In backend/app/routers/hrp.py
        from fastapi_cache.decorator import cache

        @router.post("/analyze", response_model=HRPResponse)
        @cache(expire=3600)  # Cache results for 1 hour
        async def analyze_hrp(request: HRPRequest) -> HRPResponse:
            # ... implementation ...
        ```

### **4.2. Frontend Testing**

* **Problem**: The complete absence of automated frontend testing creates significant risk.
* **Recommendation**: Implement a modern frontend testing suite using **Vitest** and **React Testing Library (RTL)**.
* **Action Plan**:
    1.  Install development dependencies: `npm install -D vitest @vitest/globals jsdom @testing-library/react @testing-library/jest-dom @testing-library/user-event`.
    2.  Update `vite.config.ts` to configure the Vitest environment.
        ```typescript
        // In frontend/vite.config.ts
        /// <reference types="vitest" />
        import { defineConfig } from 'vite';
        import react from '@vitejs/plugin-react';

        export default defineConfig({
          plugins: [react()],
          test: {
            globals: true,
            environment: 'jsdom',
            setupFiles: './src/test/setup.ts', // Path to setup file
            css: true,
          },
        });
        ```
    3.  Create a sample test file to establish a testing pattern.
        ```typescript
        // In frontend/src/components/MultiTickerSelect.test.tsx
        import { describe, test, expect, vi } from 'vitest';
        import { render, screen } from '@testing-library/react';
        import userEvent from '@testing-library/user-event';
        import MultiTickerSelect from './MultiTickerSelect';

        const mockOnChange = vi.fn();

        describe('MultiTickerSelect Component', () => {
          test('should render initial tickers passed via props', () => {
            const selectedTickers = ['AAPL', 'GOOGL'];
            render(
              <MultiTickerSelect
                selectedTickers={selectedTickers}
                onChange={mockOnChange}
              />
            );
            expect(screen.getByText('AAPL')).toBeInTheDocument();
            expect(screen.getByText('GOOGL')).toBeInTheDocument();
          });

          test('should allow a user to add a new ticker via input', async () => {
            const user = userEvent.setup();
            render(
              <MultiTickerSelect
                selectedTickers={['AAPL']}
                onChange={mockOnChange}
              />
            );
            const inputElement = screen.getByPlaceholderText('Add more tickers...');
            await user.type(inputElement, 'MSFT{enter}');
            expect(mockOnChange).toHaveBeenCalledWith(['AAPL', 'MSFT']);
          });
        });
        ```

### **4.3. DevOps & Production Readiness**

* **Problem**: The project lacks a standardized, reproducible deployment process.
* **Recommendation**: Containerize the full-stack application using **Docker** and **Docker Compose**.
* **Action Plan**:
    1.  **Backend Dockerfile**: Create a `Dockerfile` using a `python:3.10-slim` base image to build a container for the FastAPI backend.
    2.  **Frontend Dockerfile (Multi-stage)**: Create a multi-stage `Dockerfile`. The first stage will use a `node:18-alpine` image to build the static React assets. The second stage will copy these assets into a minimal `nginx:stable-alpine` image for serving.
    3.  **Root `docker-compose.yml`**: Define a `docker-compose.yml` file to orchestrate three services: `backend`, `frontend`, and `cache` (using the official `redis:7-alpine` image). This will allow the entire application stack to be launched with a single `docker-compose up` command.