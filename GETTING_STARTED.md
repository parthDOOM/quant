# Getting Started Guide

Complete setup and quickstart guide for the Quantitative Strategy & Risk Dashboard.

## Prerequisites

- **Python:** 3.10 or higher
- **Node.js:** 16 or higher  
- **npm:** 7 or higher
- **OS:** Windows (tested), macOS/Linux (should work)

## Installation

### 1. Clone Repository

```powershell
git clone <repository-url>
cd quant
```

### 2. Backend Setup

```powershell
# Navigate to backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate (Windows PowerShell)
.venv\Scripts\Activate.ps1

# Activate (Windows CMD)
.venv\Scripts\activate.bat

# Activate (macOS/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify installation
pytest  # Should show 126/126 tests passing
```

### 3. Frontend Setup

```powershell
# Navigate to frontend (from project root)
cd frontend

# Install dependencies
npm install

# Verify installation
npm run build  # Should complete without errors
```

## Running the Application

### Start Backend Server

```powershell
cd backend
.venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

**Backend available at:** http://localhost:8000  
**API Docs:** http://localhost:8000/docs

### Start Frontend Dev Server

```powershell
cd frontend
npm run dev
```

**Frontend available at:** http://localhost:5173

## Testing

### Backend Tests

```powershell
cd backend
.venv\Scripts\Activate.ps1

# Run all tests
pytest

# Run with coverage report
pytest --cov=app --cov-report=html

# Run specific test suite
pytest tests/unit/
pytest tests/integration/
pytest tests/validation/

# Verbose output
pytest -v
```

**Test Coverage:** 126 tests, 100% passing

### Frontend (Manual Testing)

Open http://localhost:5173 and test:
1. Navigation between modules
2. HRP analysis with 10+ tickers
3. StatArb pair finding
4. IV surface fetching

## Usage Guide

### Hierarchical Risk Parity

1. Click "HRP Analysis" in navigation
2. Use multi-select dropdown to add tickers (minimum 2, maximum 20)
   - Search by symbol (e.g., "AAPL") or company name (e.g., "Apple")
   - Popular tickers suggested automatically
3. Select date range using calendar pickers
4. Choose linkage method (Ward recommended for portfolio clustering)
5. Click "Run Analysis"
6. Explore results:
   - **Dendrogram:** Hover to highlight clustered assets
   - **Heatmap:** Shows reordered correlation matrix
   - Both visualizations synchronized

**Recommended Tickers:** AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA, JPM, V, WMT

### Statistical Arbitrage

1. Click "Statistical Arbitrage" in navigation
2. Enter ticker symbols (comma-separated)
3. Select date range (recommended: 1+ year for reliable results)
4. Adjust p-value threshold slider (default: 0.05)
5. Click "Find Pairs"
6. Review cointegrated pairs table:
   - Sort by p-value, hedge ratio, half-life, or correlation
   - Lower p-value = stronger cointegration
7. Click a pair row to view spread analysis:
   - Spread time series with z-score overlay
   - Trading signals (long/short/exit markers)
   - Statistics panel

**Known Cointegrated Pairs:**
- GLD/SLV (gold/silver commodities)
- PEP/KO (Pepsi/Coca-Cola)
- JPM/BAC (major banks)
- SPY/VOO (S&P 500 ETFs)

### Implied Volatility Surface

1. Click "IV Surface" in navigation
2. Type ticker symbol (autocomplete suggests popular tickers)
3. Select expiration filter:
   - **First:** Only nearest expiration (most liquid)
   - **Near Term:** ≤90 days (standard options)
   - **All:** All available expirations
4. Set minimum volume threshold (default: 10)
5. Click "Fetch Surface"
6. Analyze results:
   - **Summary Cards:** Spot price, ATM IV, put-call skew, contract count
   - **IV Range Stats:** Mean, min/max, std dev for calls/puts
   - **Data Table:** Sortable table with tabs for Calls/Puts
   - **3D Visualization:** Interactive 3D scatter plot (coming soon)

**Recommended Tickers:** AAPL, SPY, TSLA, GOOGL, NVDA

## Configuration

### Backend Environment Variables

Create `.env` file in `backend/` directory (optional):

```bash
API_TITLE="Quantitative Strategy & Risk Dashboard"
API_VERSION="1.0.0"
CORS_ORIGINS=["http://localhost:5173"]
```

### Frontend Environment

Edit `frontend/.env` (optional):

```bash
VITE_API_URL=http://localhost:8000
```

## Troubleshooting

### Backend Issues

**Problem:** `ModuleNotFoundError` when running server  
**Solution:** Ensure virtual environment is activated and dependencies installed

**Problem:** yfinance API errors  
**Solution:** Check internet connection, ticker symbols are valid, and yfinance is latest version

**Problem:** Tests failing  
**Solution:** Run `pip install -r requirements.txt` again to ensure all dependencies

### Frontend Issues

**Problem:** `npm run dev` fails  
**Solution:** Delete `node_modules/` and `package-lock.json`, then run `npm install` again

**Problem:** API calls failing  
**Solution:** Ensure backend server is running at http://localhost:8000

**Problem:** TypeScript errors  
**Solution:** Run `npm run build` to check for compilation errors

### Common Errors

**CORS Error:**
```
Access to fetch at 'http://localhost:8000' from origin 'http://localhost:5173' has been blocked by CORS policy
```
**Solution:** Backend server not running or CORS not configured. Restart backend server.

**Data Fetching Error:**
```
Failed to fetch IV surface data. Please try again.
```
**Solution:** Ticker has no options data or yfinance API issue. Try different ticker or check internet.

## Next Steps

- Explore API documentation at http://localhost:8000/docs
- Read technical architecture in [ARCHITECTURE.md](ARCHITECTURE.md)
- Check project status in [progress.md](progress.md)
- Run manual test scripts in `backend/scripts/`

## Development Tips

### Backend Development

```powershell
# Auto-reload on code changes
uvicorn app.main:app --reload --log-level debug

# Run tests on file save (using pytest-watch)
pip install pytest-watch
ptw

# Generate coverage report
pytest --cov=app --cov-report=html
# Open htmlcov/index.html in browser
```

### Frontend Development

```powershell
# Type checking
npm run type-check

# Build for production
npm run build
npm run preview  # Preview production build
```

## API Examples

### HRP Analysis (cURL)

```bash
curl -X POST "http://localhost:8000/hrp/analyze" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["AAPL", "MSFT", "GOOGL"],
    "start_date": "2023-01-01",
    "end_date": "2024-12-31",
    "linkage_method": "ward"
  }'
```

### Find Pairs (cURL)

```bash
curl -X POST "http://localhost:8000/stat-arb/find-pairs" \
  -H "Content-Type: application/json" \
  -d '{
    "tickers": ["GLD", "SLV", "PEP", "KO"],
    "start_date": "2024-01-01",
    "end_date": "2024-12-31",
    "p_value_threshold": 0.05
  }'
```

### IV Surface (cURL)

```bash
curl "http://localhost:8000/iv/surface/AAPL?expiration_filter=first&min_volume=10"
```

## Support

For issues, questions, or feature requests, please check:
1. This documentation
2. API documentation at http://localhost:8000/docs
3. Test files in `backend/tests/` for examples
4. Project architecture in [ARCHITECTURE.md](ARCHITECTURE.md)

---

**Ready to analyze! Happy trading! 📈**
