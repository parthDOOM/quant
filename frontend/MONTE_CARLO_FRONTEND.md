# Frontend Integration - Monte Carlo Simulation

## Summary
Added Monte Carlo Simulation page to showcase our blazing-fast C++ engine (9-11x speedup)!

## Files Created/Modified

### New Files
1. **`frontend/src/pages/MonteCarloSimulation.tsx`** (350 lines)
   - Full-featured simulation page
   - Form inputs: tickers, date range, num_simulations, num_days
   - Performance badge highlighting C++ acceleration
   - Results display with statistics cards
   - Equal-weighted portfolio visualization
   - Responsive design with dark mode support

### Modified Files
1. **`frontend/src/types/api.ts`**
   - Added `MonteCarloRequest` interface
   - Added `MonteCarloResponse` interface

2. **`frontend/src/services/api.ts`**
   - Added `monteCarloAPI.simulate()` function
   - Imported new types

3. **`frontend/src/App.tsx`**
   - Added `/monte-carlo` route
   - Imported `MonteCarloSimulation` component

4. **`frontend/src/pages/Dashboard.tsx`**
   - Added Monte Carlo module card
   - Imported `Activity` icon from lucide-react
   - Updated modules grid (3 → 4 modules)

## Features

### User Inputs
- **Tickers**: Comma-separated list (e.g., AAPL, MSFT, GOOGL)
- **Date Range**: Start/End dates for historical data
- **Simulations**: Number of Monte Carlo paths (100-100,000)
- **Forecast Period**: Number of trading days to simulate

### Output Display
- **Execution Time**: Shows milliseconds (demonstrates C++ speed)
- **Simulation Count**: Number of paths generated
- **Portfolio Size**: Number of assets
- **Status**: Completion indicator
- **Weights**: Equal-weighted portfolio display
- **Performance Badge**: Highlights 9-11x C++ speedup

## Technical Details

### API Integration
```typescript
interface MonteCarloRequest {
  tickers: string[];
  start_date: string;
  end_date: string;
  num_simulations: number;
  num_days: number;
}

interface MonteCarloResponse {
  simulated_prices: number[][][]; // [simulation][day][asset]
  num_simulations: number;
  num_days: number;
  num_assets: number;
  execution_time_ms: number;
}
```

### Backend Endpoint
- **URL**: `POST /monte-carlo/simulate`
- **Engine**: C++ with OpenMP parallelization
- **Performance**: 9-11x faster than Python
- **Method**: Cholesky decomposition + Geometric Brownian Motion

## Design

### Color Scheme
- **Primary**: Purple to Indigo gradient (`from-purple-500 to-indigo-600`)
- **Matches**: System color palette
- **Dark Mode**: Fully supported

### Components
- **Form**: Responsive grid layout (1 col mobile, 2 cols desktop)
- **Cards**: Statistics display with gradient text
- **Loading State**: Spinner with "Running Simulation..." text
- **Error Handling**: Red banner with error message
- **Success State**: Info cards + results display

## Next Steps (Future Enhancement)

### Visualization (Phase 2)
The page currently shows simulation results but doesn't visualize the data. Next steps:

1. **Install Plotly.js**
   ```bash
   npm install plotly.js-dist-min
   npm install @types/plotly.js --save-dev
   ```

2. **Add Fan Chart**
   - Display all simulation paths
   - Show confidence intervals (95%, 90%, 80%)
   - Interactive zoom/pan

3. **Add Histogram**
   - Final portfolio value distribution
   - Mean, median markers
   - VaR, CVaR indicators

4. **Add Statistics Table**
   - Percentiles (5th, 25th, 50th, 75th, 95th)
   - Mean, Median, Std Dev
   - Sharpe Ratio
   - Max Drawdown

## Testing

### Manual Test Steps
1. Start backend: `cd backend && uvicorn app.main:app --reload`
2. Start frontend: `cd frontend && npm run dev`
3. Navigate to: `http://localhost:5173/monte-carlo`
4. Enter tickers: `AAPL, MSFT, GOOGL`
5. Set dates: `2023-01-01` to `2024-01-01`
6. Simulations: `10000`
7. Days: `252` (1 trading year)
8. Click "Run Monte Carlo Simulation"
9. Verify execution time is fast (<100ms for 10k simulations)
10. Check results display correctly

### Expected Behavior
- Form submits without errors
- Loading spinner appears
- Results display within milliseconds
- Execution time shown (e.g., "45.23ms")
- Portfolio weights calculated correctly
- Dark mode styling works

## Status
✅ **Frontend Integration Complete**
- Page created and routed
- API integration done
- UI/UX polished
- Dark mode supported
- Performance badge added

⏳ **Visualization Pending** (Future Phase)
- Plotly.js installation needed
- Fan chart implementation
- Histogram rendering
- Statistics table

## Impact
This page showcases our C++ optimization achievements:
- Users can see **real execution times** (milliseconds!)
- **Performance badge** educates users about C++ acceleration
- **Professional UI** demonstrates platform quality
- **Responsive design** works on all devices

The Monte Carlo page is now the **flagship feature** demonstrating our hybrid C++/Python architecture! 🚀
