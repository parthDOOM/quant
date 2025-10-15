import React, { useState } from 'react';
import { ivSurfaceService } from '../services/ivSurface';
import type { IVSurfaceResponse, ExpirationFilter } from '../types/ivSurface';
import IVSummaryCards from '../components/IVSummaryCards';
import IVDataTable from '../components/IVDataTable';
import IVSurfaceChart3D from '../components/IVSurfaceChart3D';
import TickerAutocomplete from '../components/TickerAutocomplete';

const IVSurfaceAnalysis: React.FC = () => {
  const [ticker, setTicker] = useState<string>('');
  const [expirationFilter, setExpirationFilter] = useState<ExpirationFilter>('first');
  const [minVolume, setMinVolume] = useState<number>(10);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<IVSurfaceResponse | null>(null);

  const handleFetchSurface = async () => {
    if (!ticker.trim()) {
      setError('Please enter a ticker symbol');
      return;
    }

    setLoading(true);
    setError(null);
    setData(null);

    try {
      const response = await ivSurfaceService.fetchIVSurface(
        ticker.trim().toUpperCase(),
        expirationFilter,
        minVolume
      );
      setData(response);
    } catch (err) {
      const error = err as { response?: { status?: number; data?: { message?: string } } };
      if (error.response?.status === 404) {
        setError(`Ticker "${ticker.toUpperCase()}" not found or has no options data`);
      } else if (error.response?.data?.message) {
        setError(error.response.data.message);
      } else {
        setError('Failed to fetch IV surface data. Please try again.');
      }
      console.error('Error fetching IV surface:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-8 max-w-7xl mx-auto">
      {/* Header */}
      <div className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          Implied Volatility Surface
        </h1>
        <p className="text-slate-300">
          Analyze option implied volatilities using Black-Scholes-Merton with Newton-Raphson solver
        </p>
      </div>

      {/* Controls */}
      <div className="relative z-40 bg-slate-800/50 backdrop-blur-lg rounded-xl shadow-xl border border-slate-700 p-6 mb-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {/* Ticker Input with Autocomplete */}
          <div className="relative z-50">
            <label htmlFor="ticker" className="block text-sm font-medium text-slate-300 mb-2">
              Ticker Symbol
            </label>
            <TickerAutocomplete
              value={ticker}
              onChange={setTicker}
              onSelect={(symbol) => {
                setTicker(symbol);
                // Optional: Auto-fetch on selection
                // handleFetchSurface();
              }}
              disabled={loading}
            />
          </div>

          {/* Expiration Filter */}
          <div>
            <label htmlFor="expiration" className="block text-sm font-medium text-slate-300 mb-2">
              Expiration Filter
            </label>
            <select
              id="expiration"
              value={expirationFilter}
              onChange={(e) => setExpirationFilter(e.target.value as ExpirationFilter)}
              className="w-full px-4 py-2 bg-slate-900/50 border border-slate-600 text-white rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent"
              disabled={loading}
            >
              <option value="first">First (Nearest)</option>
              <option value="near_term">Near Term (≤90 days)</option>
              <option value="all">All Expirations</option>
            </select>
          </div>

          {/* Volume Filter */}
          <div>
            <label htmlFor="volume" className="block text-sm font-medium text-slate-300 mb-2">
              Min Volume: {minVolume}
            </label>
            <input
              id="volume"
              type="range"
              min="0"
              max="1000"
              step="10"
              value={minVolume}
              onChange={(e) => setMinVolume(Number(e.target.value))}
              className="w-full"
              disabled={loading}
            />
            <div className="flex justify-between text-xs text-slate-400 mt-1">
              <span>0</span>
              <span>500</span>
              <span>1000</span>
            </div>
          </div>

          {/* Fetch Button */}
          <div className="flex items-end">
            <button
              onClick={handleFetchSurface}
              disabled={loading}
              className={`w-full px-6 py-2 rounded-lg font-semibold text-white transition-colors ${
                loading
                  ? 'bg-gray-400 cursor-not-allowed'
                  : 'bg-teal-600 hover:bg-teal-700 active:bg-teal-800'
              }`}
            >
              {loading ? (
                <span className="flex items-center justify-center">
                  <svg className="animate-spin h-5 w-5 mr-2" viewBox="0 0 24 24">
                    <circle
                      className="opacity-25"
                      cx="12"
                      cy="12"
                      r="10"
                      stroke="currentColor"
                      strokeWidth="4"
                      fill="none"
                    />
                    <path
                      className="opacity-75"
                      fill="currentColor"
                      d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"
                    />
                  </svg>
                  Loading...
                </span>
              ) : (
                '🔍 Fetch Surface'
              )}
            </button>
          </div>
        </div>

        {/* Info */}
        <div className="mt-4 p-3 bg-slate-700/50 border border-slate-600 rounded-lg">
          <p className="text-xs text-slate-300">
            <strong>💡 Tip:</strong> First expiration contains the most liquid contracts. Increase minimum volume to filter out
            illiquid options. IV is calculated using Newton-Raphson method (converges in ~5-8 iterations for liquid options).
          </p>
        </div>
      </div>

      {/* Error Message */}
      {error && (
        <div className="bg-red-50 border-l-4 border-red-500 p-4 mb-8 rounded-r-lg">
          <div className="flex items-center">
            <span className="text-2xl mr-3">⚠️</span>
            <div>
              <p className="text-sm font-medium text-red-800">Error</p>
              <p className="text-sm text-red-700">{error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results */}
      {data && (
        <>
          {/* Summary Cards */}
          <IVSummaryCards spotPrice={data.spot_price} metrics={data.metrics} />

          {/* Metrics Info */}
          <div className="mb-6 grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="bg-gradient-to-r from-teal-900/40 to-teal-800/40 backdrop-blur-lg border border-teal-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-teal-300 mb-2">📊 Call Options IV Range</h3>
              <div className="text-xs text-teal-200 space-y-1">
                <p>
                  <strong>Mean:</strong>{' '}
                  {data.metrics.iv_range_calls.mean !== null
                    ? `${(data.metrics.iv_range_calls.mean * 100).toFixed(2)}%`
                    : 'N/A'}
                </p>
                <p>
                  <strong>Range:</strong>{' '}
                  {data.metrics.iv_range_calls.min !== null && data.metrics.iv_range_calls.max !== null
                    ? `${(data.metrics.iv_range_calls.min * 100).toFixed(2)}% - ${(data.metrics.iv_range_calls.max * 100).toFixed(2)}%`
                    : 'N/A'}
                </p>
                <p>
                  <strong>Std Dev:</strong>{' '}
                  {data.metrics.iv_range_calls.std !== null
                    ? `${(data.metrics.iv_range_calls.std * 100).toFixed(2)}%`
                    : 'N/A'}
                </p>
                <p>
                  <strong>Success Rate:</strong>{' '}
                  {data.metrics.total_call_contracts > 0
                    ? `${((data.metrics.successful_call_ivs / data.metrics.total_call_contracts) * 100).toFixed(1)}%`
                    : 'N/A'}
                </p>
              </div>
            </div>

            <div className="bg-gradient-to-r from-amber-900/40 to-amber-800/40 backdrop-blur-lg border border-amber-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-amber-300 mb-2">📉 Put Options IV Range</h3>
              <div className="text-xs text-amber-200 space-y-1">
                <p>
                  <strong>Mean:</strong>{' '}
                  {data.metrics.iv_range_puts.mean !== null
                    ? `${(data.metrics.iv_range_puts.mean * 100).toFixed(2)}%`
                    : 'N/A'}
                </p>
                <p>
                  <strong>Range:</strong>{' '}
                  {data.metrics.iv_range_puts.min !== null && data.metrics.iv_range_puts.max !== null
                    ? `${(data.metrics.iv_range_puts.min * 100).toFixed(2)}% - ${(data.metrics.iv_range_puts.max * 100).toFixed(2)}%`
                    : 'N/A'}
                </p>
                <p>
                  <strong>Std Dev:</strong>{' '}
                  {data.metrics.iv_range_puts.std !== null
                    ? `${(data.metrics.iv_range_puts.std * 100).toFixed(2)}%`
                    : 'N/A'}
                </p>
                <p>
                  <strong>Success Rate:</strong>{' '}
                  {data.metrics.total_put_contracts > 0
                    ? `${((data.metrics.successful_put_ivs / data.metrics.total_put_contracts) * 100).toFixed(1)}%`
                    : 'N/A'}
                </p>
              </div>
            </div>
          </div>

          {/* Expirations */}
          {data.metrics.expiration_dates.length > 0 && (
            <div className="mb-6 bg-indigo-900/40 backdrop-blur-lg border border-indigo-700 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-indigo-300 mb-2">📅 Expiration Dates</h3>
              <div className="flex flex-wrap gap-2">
                {data.metrics.expiration_dates.map((date, index) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-indigo-800/50 text-indigo-200 text-xs font-medium rounded-full border border-indigo-600"
                  >
                    {date}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Data Table */}
          <IVDataTable calls={data.calls} puts={data.puts} />

          {/* 3D Surface Chart */}
          <div className="mt-8">
            <IVSurfaceChart3D 
              calls={data.calls} 
              puts={data.puts} 
              spotPrice={data.spot_price} 
            />
          </div>

          {/* Methodology Note */}
          <div className="mt-6 bg-slate-800/50 backdrop-blur-lg border border-slate-700 rounded-lg p-4">
            <h3 className="text-sm font-semibold text-slate-200 mb-2">📚 Methodology</h3>
            <div className="text-xs text-slate-300 space-y-1">
              <p>
                <strong>Pricing Model:</strong> Black-Scholes-Merton for European options
              </p>
              <p>
                <strong>IV Solver:</strong> Newton-Raphson iterative method (tolerance: 1e-6, max iterations: 100)
              </p>
              <p>
                <strong>Risk-Free Rate:</strong> {(data.risk_free_rate * 100).toFixed(2)}% (current 10-year Treasury)
              </p>
              <p>
                <strong>Data Source:</strong> Yahoo Finance via yfinance
              </p>
              <p>
                <strong>Note:</strong> Deep ITM/OTM options may fail to converge due to low Vega (&lt;1e-8). This is
                mathematically correct behavior.
              </p>
            </div>
          </div>
        </>
      )}

      {/* Empty State */}
      {!data && !error && !loading && (
        <div className="bg-slate-800/30 backdrop-blur-lg border-2 border-dashed border-slate-700 rounded-xl p-12 text-center">
          <div className="text-6xl mb-4">📈</div>
          <h3 className="text-xl font-semibold text-white mb-2">Ready to Analyze</h3>
          <p className="text-slate-400">
            Enter a ticker symbol and click "Fetch Surface" to calculate implied volatilities
          </p>
          <div className="mt-6 flex justify-center gap-4">
            <button
              onClick={() => {
                setTicker('AAPL');
                setTimeout(handleFetchSurface, 100);
              }}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-sm font-medium transition-colors"
            >
              Try AAPL
            </button>
            <button
              onClick={() => {
                setTicker('SPY');
                setTimeout(handleFetchSurface, 100);
              }}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-sm font-medium transition-colors"
            >
              Try SPY
            </button>
            <button
              onClick={() => {
                setTicker('TSLA');
                setTimeout(handleFetchSurface, 100);
              }}
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-slate-200 rounded-lg text-sm font-medium transition-colors"
            >
              Try TSLA
            </button>
          </div>
        </div>
      )}
    </div>
  );
};

export default IVSurfaceAnalysis;
