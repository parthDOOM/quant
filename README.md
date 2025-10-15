# Quantitative Strategy & Risk Dashboard 📊 Quantitative Strategy & Risk Dashboard# Quantitative Strategy & Risk Dashboard



A comprehensive web application for portfolio optimization, statistical arbitrage analysis, and options implied volatility surface visualization. Built with modern technologies and financial mathematics.



[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)A professional full-stack web application for quantitative portfolio analysis, featuring three powerful analytical modules.A modular, full-stack quantitative analysis web application for portfolio optimization, statistical arbitrage, and options risk assessment.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)

[![React](https://img.shields.io/badge/React-18%2B-61DAFB)](https://react.dev/)

[![TypeScript](https://img.shields.io/badge/TypeScript-5%2B-3178C6)](https://www.typescriptlang.org/)

[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)## 🎯 Features## 🎯 Overview



## 🚀 Features



### 📈 Hierarchical Risk Parity (HRP)### Phase 1: HRP AnalysisThis application provides three sophisticated analytical modules:

- **Portfolio optimization** using hierarchical clustering

- **Interactive dendrogram** visualization showing asset relationships- Multi-ticker portfolio optimization using hierarchical clustering

- **Correlation heatmap** with synchronized hover effects

- **Multiple linkage methods** (Ward, Single, Complete, Average)- Interactive dendrogram and correlation heatmap visualizations1. **Hierarchical Risk Parity (HRP) Analyzer** - Visualize asset correlation structures through interactive dendrograms and heatmaps

- Exports cluster-based allocation strategies

- 4 linkage methods: Ward, Single, Complete, Average2. **Statistical Arbitrage Pair Finder** - Identify cointegrated asset pairs for mean-reversion strategies

### 🔄 Statistical Arbitrage

- **Cointegration testing** (Engle-Granger method)- Multi-ticker autocomplete with search3. **Implied Volatility Surface Visualizer** - 3D visualization of options volatility surfaces

- **Pairs trading** signal generation with z-score thresholds

- **Spread analysis** with entry/exit signals

- **Interactive charts** with dual-axis price/spread visualization

- Hedge ratio and half-life calculations### Phase 2: Statistical Arbitrage  ## 🏗️ Architecture



### 📊 Implied Volatility Surface- Engle-Granger cointegration testing for pair trading

- **3D surface visualization** of options IV across strikes and expirations

- **Real-time options data** from Yahoo Finance- Spread analysis with z-score and trading signals- **Backend**: Python 3.10+ with FastAPI

- **Black-Scholes-Merton** pricing with Newton-Raphson IV solver

- **IV metrics:** ATM IV, IV skew, IV range- Interactive dual-axis spread chart- **Frontend**: React 18+ with TypeScript

- Filterable by expiration date and trading volume

- Automated hedge ratio calculation- **Visualization**: D3.js (2D) and Plotly.js (3D)

## 🛠️ Tech Stack

- **Data**: yfinance, pandas, numpy, scipy, statsmodels

**Backend:**

- FastAPI (Python async web framework)### Phase 3: Implied Volatility- **Cache**: Redis

- scipy (hierarchical clustering, optimization)

- statsmodels (cointegration testing)- Black-Scholes-Merton options pricing- **Database**: PostgreSQL (for user data and analysis persistence)

- yfinance (market data)

- pandas, numpy (data processing)- Newton-Raphson IV solver (converges in 5-8 iterations)- **Auth**: JWT tokens for multi-user support

- pytest (testing - 126 tests, 100% passing)

- Volatility surface visualization with 3D scatter plot

**Frontend:**

- React 18 + TypeScript- ATM IV tracking and put-call skew analysis## 📁 Project Structure

- React Router (SPA navigation)

- D3.js (dendrograms, heatmaps, line charts)

- Plotly.js (3D surface plots)

- TailwindCSS + shadcn/ui (styling)## 🛠 Tech Stack```

- Vite (build tool)

quant/

**Data Sources:**

- Yahoo Finance API (historical prices, options chains, risk-free rate)**Backend:** Python 3.10+, FastAPI, yfinance, pandas, scipy, statsmodels  ├── backend/                    # Python FastAPI backend



**Testing:****Frontend:** React 18, TypeScript, Vite, TailwindCSS, D3.js, Plotly.js  ├── frontend/                   # React TypeScript frontend

- pytest (backend unit, integration, validation tests)

- FastAPI TestClient (API testing)**Testing:** pytest (126 tests, 100% passing)├── docs/                       # Documentation



**Visualization:**├── plan.md                     # Implementation plan

- D3.js (2D charts with custom interactions)

- Plotly.js (3D interactive plots)## 🚀 Quick Start├── progress.md                 # Progress tracking

- react-datepicker (date range selection)

└── README.md                   # This file

## ⚡ Quick Start

### Backend```

```bash

# Clone repository```powershell

git clone https://github.com/yourusername/quant-dashboard.git

cd quant-dashboardcd backend## 🚀 Quick Start



# Backend setuppython -m venv .venv

cd backend

python -m venv .venv.venv\Scripts\Activate.ps1### Prerequisites

.venv\Scripts\activate          # Windows

pip install -r requirements.txtpip install -r requirements.txt

uvicorn app.main:app --reload   # Runs on http://localhost:8000

uvicorn app.main:app --reload- Python 3.10+

# Frontend setup (in new terminal)

cd frontend```- Node.js 18+

npm install

npm run dev                     # Runs on http://localhost:5173**Server:** http://localhost:8000- Redis server

```

- PostgreSQL (optional for Phase 1)

## 📚 Documentation

### Frontend

- **[Getting Started](GETTING_STARTED.md)** - Installation, setup, and troubleshooting

- **[Architecture](ARCHITECTURE.md)** - Technical documentation and API reference```powershell### Backend Setup



## 🧩 Modulescd frontend



### HRP Modulenpm install```powershell

Uses hierarchical clustering to group assets based on correlation distance, then applies recursive bisection for risk-balanced portfolio allocation. Visualizes asset relationships through dendrograms and reordered correlation matrices.

npm run devcd backend

### StatArb Module

Implements Engle-Granger cointegration testing to identify statistically arbitrageable pairs. Generates trading signals based on z-score thresholds applied to normalized spreads. Calculates hedge ratios and mean reversion speeds.```



### IV Surface Module**App:** http://localhost:5173# Create and activate virtual environment

Fetches live options chains and calculates implied volatility using Newton-Raphson numerical method on Black-Scholes-Merton formula. Visualizes IV across strike prices and expiration dates in interactive 3D space.

python -m venv .venv

## 📄 License

## 📊 Project Status.\.venv\Scripts\Activate.ps1

MIT License - see [LICENSE](LICENSE) file for details.



## 📧 Contact

- **Phase 1 (HRP):** ✅ 100% Complete# Install dependencies

For questions or collaboration:

- GitHub Issues: [Create an issue](https://github.com/yourusername/quant-dashboard/issues)- **Phase 2 (StatArb):** ✅ 100% Completepip install -r requirements.txt

- Email: your.email@example.com

- **Phase 3 (IV):** 🔄 95% Complete

---

- **Tests:** 126/126 passing (100%)# Run development server

**Built with ❤️ for quantitative finance enthusiasts**

uvicorn app.main:app --reload

## 📚 Documentation```



- **Setup Guide:** See [GETTING_STARTED.md](GETTING_STARTED.md)Backend will run on `http://localhost:8000`

- **Architecture:** See [ARCHITECTURE.md](ARCHITECTURE.md)

- **API Docs:** http://localhost:8000/docs (when running)### Frontend Setup



## 📁 Project Structure```powershell

cd frontend

```

quant/# Install dependencies

├── backend/              # FastAPI servernpm install

│   ├── app/             # Application code

│   ├── tests/           # pytest test suite# Run development server

│   └── scripts/         # Manual test scriptsnpm run dev

├── frontend/            # React application```

│   └── src/            # Source code

└── docs/               # DocumentationFrontend will run on `http://localhost:5173` (Vite dev server)

```

## 📚 Documentation

## 🧪 Testing

- See `plan.md` for comprehensive implementation details

```powershell- See `progress.md` for development tracking and status

cd backend- API documentation available at `http://localhost:8000/docs` when backend is running

pytest                    # Run all tests

pytest --cov=app         # With coverage## 🧪 Testing

```

**Test Status**: 61/61 passing (100%) ✅

## 🤝 Contributing

### Backend Tests

Suggestions and feedback welcome!```powershell

cd backend

## 📄 License.\.venv\Scripts\Activate.ps1  # Activate virtual environment



MIT License# Run all tests

pytest tests/ -v

---

# Run specific test suites

**Built with Python, FastAPI, React, and TypeScript**pytest tests/unit/test_data_ingestion.py -v

pytest tests/unit/test_hrp_clustering.py -v
pytest tests/unit/test_cointegration.py -v
pytest tests/integration/test_api.py -v
```

**Current Results**:
- HRP Tests: 50/50 passing
- StatArb Tests: 11/11 passing

### Frontend Tests
```powershell
cd frontend
npm test
```

*Note: Frontend tests to be implemented*

## 🔧 Development

**Current Status**: Phase 2 Complete - 67% Total Progress 🎉

### ✅ Phase 1: HRP Portfolio Analyzer - COMPLETE (100%)
- Backend API with correlation matrix and hierarchical clustering
- React frontend with interactive D3.js dendrogram and heatmap
- Enhanced calendar component with react-datepicker
- 50/50 tests passing

### ✅ Phase 2: Statistical Arbitrage - COMPLETE (100%)
- ✅ Backend: Cointegration testing service (100% complete)
- ✅ Backend: 3 API endpoints for pair testing (100% complete)
- ✅ Backend: 11/11 tests passing
- ✅ Frontend: StatArb UI with sortable table and D3.js charts (100% complete)
- ✅ Full-stack integration working end-to-end

### ⏳ Phase 3: Implied Volatility - NOT STARTED (0%)
- Options chain data ingestion
- Black-Scholes-Merton pricing
- 3D volatility surface visualization
- Greeks calculator

See `PROJECT_STATUS.md` for comprehensive project overview and `progress.md` for detailed development tracking.

## 📝 License

MIT License - See LICENSE file for details

## 👥 Contributors

Development started: October 15, 2025
