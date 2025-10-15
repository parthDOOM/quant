# Backend README

## Setup

### 1. Create Virtual Environment

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

### 2. Install Dependencies

```powershell
pip install -r requirements.txt
```

### 3. Configure Environment

Copy `.env.example` to `.env` and update values:

```powershell
Copy-Item .env.example .env
```

Edit `.env` with your configuration.

### 4. Run Development Server

```powershell
python -m uvicorn app.main:app --reload
```

Or simply:

```powershell
python app/main.py
```

The API will be available at:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Alternative docs: http://localhost:8000/redoc

## Project Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic models (request/response schemas)
│   ├── services/            # Business logic layer
│   ├── routers/             # API route handlers
│   └── utils/               # Utility functions
├── tests/
│   ├── unit/                # Unit tests
│   ├── integration/         # Integration tests
│   └── validation/          # Validation tests
├── requirements.txt         # Python dependencies
└── .env.example            # Example environment configuration
```

## Running Tests

```powershell
# Run all tests
pytest

# Run with coverage
pytest --cov=app tests/

# Run specific test file
pytest tests/unit/test_data_ingestion.py -v

# Run with detailed output
pytest -vv
```

## API Endpoints

### Health Check
- `GET /` - Basic health check
- `GET /health` - Detailed health check

### Phase 1: HRP Analysis (Coming Soon)
- `POST /hrp/analyze` - Perform HRP analysis
- `GET /hrp/clusters/{cluster_id}` - Get cluster assets

### Phase 2: Statistical Arbitrage (Coming Soon)
- `GET /stat-arb/find_pairs/{cluster_id}` - Find cointegrated pairs

### Phase 3: Implied Volatility (Coming Soon)
- `GET /iv/surface/{ticker}` - Get IV surface data

## Development

### Code Style

We use:
- `black` for code formatting
- `flake8` for linting
- `mypy` for type checking
- `isort` for import sorting

Run formatters:

```powershell
black app/ tests/
isort app/ tests/
flake8 app/ tests/
mypy app/
```

## Dependencies

Key libraries:
- **FastAPI**: Web framework
- **yfinance**: Market data
- **pandas/numpy**: Data processing
- **scipy**: Hierarchical clustering
- **statsmodels**: Cointegration tests
- **redis**: Caching layer
- **SQLAlchemy**: Database ORM

See `requirements.txt` for complete list.
