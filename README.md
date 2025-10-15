# Quantitative Strategy & Risk Dashboard 📊

A professional full-stack web application for quantitative portfolio analysis, statistical arbitrage, and options risk assessment. Built with modern financial mathematics and interactive visualizations.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-green)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18%2B-61DAFB)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/TypeScript-5%2B-3178C6)](https://www.typescriptlang.org/)
[![Tests](https://img.shields.io/badge/Tests-126%2F126%20passing-brightgreen)](https://github.com/parthDOOM/quant)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 🎯 Overview

This application provides three sophisticated analytical modules for quantitative finance:

1. **Hierarchical Risk Parity (HRP) Analyzer** - Portfolio optimization using hierarchical clustering with interactive dendrograms and correlation heatmaps
2. **Statistical Arbitrage Pair Finder** - Identify cointegrated asset pairs for mean-reversion trading strategies
3. **Implied Volatility Surface Visualizer** - 3D visualization of options volatility surfaces with Black-Scholes-Merton pricing

## 🚀 Features

### 📈 Hierarchical Risk Parity (HRP)

- Multi-ticker portfolio optimization using hierarchical clustering
- Interactive dendrogram visualization showing asset relationships
- Correlation heatmap with synchronized hover effects
- Multiple linkage methods: Ward, Single, Complete, Average
- Exports cluster-based allocation strategies

### 🔄 Statistical Arbitrage

- Engle-Granger cointegration testing for pair trading
- Spread analysis with z-score and trading signals
- Interactive dual-axis price/spread chart
- Automated hedge ratio and half-life calculations
- Multi-ticker autocomplete with search

### 📊 Implied Volatility Surface

- Black-Scholes-Merton options pricing
- Newton-Raphson IV solver (converges in 5-8 iterations)
- 3D surface visualization with Plotly.js
- ATM IV tracking and put-call skew analysis
- Filterable by expiration date and trading volume

## 🛠️ Tech Stack

**Backend:**

- FastAPI (Python async web framework)
- scipy (hierarchical clustering, optimization)
- statsmodels (cointegration testing)
- yfinance (market data from Yahoo Finance)
- pandas, numpy (data processing)
- pytest (126 tests, 100% passing)

**Frontend:**

- React 18 + TypeScript
- React Router (SPA navigation)
- D3.js (dendrograms, heatmaps, line charts)
- Plotly.js (3D surface plots)
- TailwindCSS + shadcn/ui (styling)
- Vite (build tool)

**Data Sources:**

- Yahoo Finance API (historical prices, options chains, risk-free rate)

## 📁 Project Structure

```
quant/
├── backend/                    # Python FastAPI backend
│   ├── app/
│   │   ├── main.py            # Application entry point
│   │   ├── config.py          # Configuration
│   │   ├── models/            # Pydantic models
│   │   ├── routers/           # API endpoints
│   │   └── services/          # Business logic
│   ├── tests/                 # pytest test suite
│   │   ├── unit/              # Unit tests
│   │   ├── integration/       # Integration tests
│   │   └── validation/        # Validation tests
│   └── requirements.txt       # Python dependencies
├── frontend/                   # React TypeScript frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── pages/             # Page components
│   │   └── utils/             # Utility functions
│   └── package.json           # Node.js dependencies
├── ARCHITECTURE.md            # Technical documentation
├── GETTING_STARTED.md         # Setup guide
└── README.md                  # This file
```

## ⚡ Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+

### Backend Setup

```powershell
cd backend

# Create and activate virtual environment
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt

# Run development server
uvicorn app.main:app --reload
```

Backend will run on `http://localhost:8000`

### Frontend Setup

```powershell
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

Frontend will run on `http://localhost:5173` (Vite dev server)

## 📚 Documentation

- **[Getting Started](GETTING_STARTED.md)** - Installation, setup, and troubleshooting
- **[Architecture](ARCHITECTURE.md)** - Technical documentation and system design
- **API Docs:** http://localhost:8000/docs (interactive Swagger UI when backend is running)

## 🧪 Testing

**Test Status**: 126/126 passing (100%) ✅

### Backend Tests

```powershell
cd backend
.\.venv\Scripts\Activate.ps1

# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ --cov=app --cov-report=html

# Run specific test suites
pytest tests/unit/ -v
pytest tests/integration/ -v
pytest tests/validation/ -v
```

**Test Breakdown:**

- Unit tests: Data ingestion, HRP clustering, cointegration analysis
- Integration tests: API endpoints, full-stack workflows
- Validation tests: Correlation calculations, financial mathematics

## 🧩 Module Details

### HRP Module

Uses hierarchical clustering to group assets based on correlation distance, then applies recursive bisection for risk-balanced portfolio allocation. Visualizes asset relationships through dendrograms and reordered correlation matrices.

### StatArb Module

Implements Engle-Granger cointegration testing to identify statistically arbitrageable pairs. Generates trading signals based on z-score thresholds applied to normalized spreads. Calculates hedge ratios and mean reversion speeds.

### IV Surface Module

Fetches live options chains and calculates implied volatility using Newton-Raphson numerical method on Black-Scholes-Merton formula. Visualizes IV across strike prices and expiration dates in interactive 3D space.

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/parthDOOM/quant/issues).

## 📄 License

MIT License - See [LICENSE](LICENSE) file for details.

---

**Built with ❤️ for quantitative finance enthusiasts**

Repository: https://github.com/parthDOOM/quant
