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

Edit `.env` with your configuration:

```properties
# Data Provider (Polygon.io API key)
POLYGON_API_KEY=your_polygon_api_key_here
DATA_PROVIDER=auto  # Options: polygon, yfinance, auto

# Redis
REDIS_URL=redis://localhost:6379

# Security (change in production)
SECRET_KEY=your-secret-key-change-this-in-production
```

**Getting a Polygon API Key:**
1. Sign up at https://polygon.io/
2. Free tier: 5 requests/minute
3. Copy API key from dashboard
4. Add to `.env` file

**Note:** Without Polygon API key, system will use yfinance as fallback.

### 3.5. Redis Setup

Redis is required for caching. Install and run using Docker:

```powershell
# Pull Redis image
docker pull redis:7-alpine

# Start Redis container
docker run -d --name quant-redis -p 6379:6379 redis:7-alpine

# Verify Redis is running
docker ps --filter name=quant-redis
```

**Without Docker:**
- Download Redis from https://redis.io/download
- Install and start Redis server on port 6379
- Windows: Use WSL or Redis for Windows

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

### HRP Analysis ✅
- `POST /hrp/correlation` - Calculate correlation matrix (cached 60min)
- `POST /hrp/analyze` - Perform HRP analysis (cached 60min)

### Statistical Arbitrage ✅
- `POST /statarb/pair-cointegration` - Test pair cointegration
- `POST /statarb/find-pairs` - Find cointegrated pairs (cached 30min)
- `POST /statarb/spread-analysis` - Analyze pair spread

### Implied Volatility ✅
- `POST /iv/surface` - Get IV surface data (cached 15min, dynamic risk-free rate)

## Provider Abstraction Layer

The backend uses a provider abstraction layer (~970 lines) with automatic fallback:

**Architecture:**
```
API Endpoint
  ↓
DataProviderInterface
  ├─ PolygonProvider (primary, institutional-grade data)
  └─ YfinanceProvider (fallback, backup provider)
```

**Files:**
- `app/services/provider_interface.py` - Abstract interface and fallback logic
- `app/services/polygon_provider.py` - Polygon.io implementation
- `app/services/yfinance_provider.py` - yfinance implementation
- `app/services/provider_factory.py` - Factory pattern with dependency injection
- `app/services/economic_data.py` - Dynamic risk-free rate from U.S. Treasury

**Features:**
- Automatic fallback from Polygon to yfinance on errors
- Dynamic risk-free rate (4.187% current, updates every 12 hours)
- Redis caching with custom key builders
- Parameter-aware cache keys for POST requests

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
