import { useState, useEffect } from 'react';
import { fetchDateRange } from '../services/dateRange';
import type { DateRangeResponse } from '../services/dateRange';
import { Activity, TrendingUp, Zap } from 'lucide-react';
import { monteCarloAPI } from '../services/api';
import type { MonteCarloRequest, MonteCarloResponse } from '../types/api';
import DatePickerWrapper from './_DatePickerWrapper';

import MultiTickerSelect from '../components/MultiTickerSelect';


export default function MonteCarloSimulation() {
  const [request, setRequest] = useState<MonteCarloRequest>({
    tickers: ['AAPL', 'MSFT', 'GOOGL'],
    start_date: '2023-01-01',
    end_date: '2024-01-01',
    num_simulations: 10000,
    num_days: 252, // 1 trading year
    weighting: 'min_var',
  });
  const [response, setResponse] = useState<MonteCarloResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [dateRange, setDateRange] = useState<DateRangeResponse | null>(null);
  const [dateLoading, setDateLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const result = await monteCarloAPI.simulate(request);
      setResponse(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to run simulation');
      console.error('Monte Carlo Error:', err);
    } finally {
      setLoading(false);
    }
  };


  // Fetch available date range when tickers change
  useEffect(() => {
    if (request.tickers.length === 0) {
      setDateRange(null);
      return;
    }
    setDateLoading(true);
    fetchDateRange(request.tickers)
      .then((range) => {
        setDateRange(range);
        // Clamp start/end date if out of range
        setRequest((prev) => ({
          ...prev,
          start_date:
            prev.start_date < range.min_date || prev.start_date > range.max_date
              ? range.min_date
              : prev.start_date,
          end_date:
            prev.end_date > range.max_date || prev.end_date < range.min_date
              ? range.max_date
              : prev.end_date,
        }));
      })
      .catch(() => {
        setDateRange(null);
      })
      .finally(() => setDateLoading(false));
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [request.tickers.join(',')]);


  // Handler for MultiTickerSelect
  const handleTickersChange = (tickers: string[]) => {
    setRequest((prev) => ({ ...prev, tickers }));
  };

  return (
    <div className="container mx-auto px-4 py-8">
      {/* Header */}
      <div className="mb-8">
        <div className="flex items-center gap-3 mb-4">
          <div className="p-3 bg-gradient-to-br from-purple-500 to-indigo-600 rounded-lg">
            <Activity className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
              Monte Carlo Simulation
            </h1>
            <p className="text-gray-600 dark:text-gray-400 mt-1">
              High-performance portfolio simulation using C++ engine (9-11x faster) ⚡
            </p>
          </div>
        </div>

        {/* Performance Badge */}
        <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-50 dark:bg-green-900/20 border border-green-200 dark:border-green-800 rounded-lg">
          <Zap className="w-4 h-4 text-green-600 dark:text-green-400" />
          <span className="text-sm font-medium text-green-700 dark:text-green-300">
            C++ Accelerated • 9-11x Speedup • OpenMP Parallelized
          </span>
        </div>
      </div>

      {/* Input Form */}
      <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 mb-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">

            {/* Tickers */}
            <div className="md:col-span-2">
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Portfolio Tickers
              </label>
              <MultiTickerSelect
                selectedTickers={request.tickers}
                onChange={handleTickersChange}
                disabled={loading}
                maxSelections={20}
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Search and select ticker symbols (minimum 1, maximum 20)
              </p>
            </div>

            {/* Date Range */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Start Date
              </label>
              <DatePickerWrapper
                value={request.start_date}
                onChange={(date) => setRequest({ ...request, start_date: date })}
                min={dateRange?.min_date}
                max={dateRange?.max_date}
                disabled={dateLoading}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                End Date
              </label>
              <DatePickerWrapper
                value={request.end_date}
                onChange={(date) => setRequest({ ...request, end_date: date })}
                min={dateRange?.min_date}
                max={dateRange?.max_date}
                disabled={dateLoading}
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500"
              />
            {dateLoading && (
              <div className="col-span-2 text-sm text-gray-500 dark:text-gray-400">
                Loading available date range for selected tickers...
              </div>
            )}
            {dateRange && !dateLoading && (
              <div className="col-span-2 text-xs text-gray-500 dark:text-gray-400">
                Data available from <b>{dateRange.min_date}</b> to <b>{dateRange.max_date}</b> for all selected tickers.
              </div>
            )}
            </div>

            {/* Simulation Parameters */}
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Number of Simulations
              </label>
              <input
                type="number"
                value={request.num_simulations}
                onChange={(e) =>
                  setRequest({ ...request, num_simulations: parseInt(e.target.value) || 1000 })
                }
                min="100"
                max="100000"
                step="1000"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500"
                required
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                Recommended: 10,000 for fast results
              </p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                Number of Days (Forecast Period)
              </label>
              <input
                type="number"
                value={request.num_days}
                onChange={(e) =>
                  setRequest({ ...request, num_days: parseInt(e.target.value) || 30 })
                }
                min="1"
                max="1000"
                className="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-700 text-gray-900 dark:text-gray-100 focus:ring-2 focus:ring-purple-500"
                required
              />
              <p className="text-sm text-gray-500 dark:text-gray-400 mt-1">
                252 days = 1 trading year
              </p>
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={loading || request.tickers.length === 0}
            className="w-full md:w-auto px-8 py-3 bg-gradient-to-r from-purple-500 to-indigo-600 text-white font-semibold rounded-lg hover:from-purple-600 hover:to-indigo-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center justify-center gap-2"
          >
            {loading ? (
              <>
                <div className="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin" />
                Running Simulation...
              </>
            ) : (
              <>
                <TrendingUp className="w-5 h-5" />
                Run Monte Carlo Simulation
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error Display */}
      {error && (
        <div className="bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg p-4 mb-8">
          <p className="text-red-800 dark:text-red-200">{error}</p>
        </div>
      )}

      {/* Results */}
      {response && (
        <div className="space-y-8">
          {/* Always show Debug Info at the top for troubleshooting */}
          <div className="bg-yellow-50 dark:bg-yellow-900/20 border border-yellow-200 dark:border-yellow-800 rounded-lg p-4 mb-8">
            <h3 className="text-lg font-semibold text-yellow-900 dark:text-yellow-100 mb-2">Simulation Debug Inputs</h3>
            <div className="text-xs text-yellow-800 dark:text-yellow-200">
              <div><b>mean_returns:</b> {JSON.stringify(response.debug_inputs?.mean_returns)}</div>
              <div><b>cov_matrix:</b> {JSON.stringify(response.debug_inputs?.cov_matrix)}</div>
              <div><b>initial_prices:</b> {JSON.stringify(response.debug_inputs?.initial_prices)}</div>
              <div><b>portfolio_weights:</b> {JSON.stringify(response.debug_inputs?.portfolio_weights)}</div>
              <div><b>raw_prices:</b> {JSON.stringify(response.debug_inputs?.raw_prices)}</div>
              {(!response.debug_inputs?.raw_prices || Object.keys(response.debug_inputs?.raw_prices).length === 0) && (
                <div className="mt-2 text-red-700 dark:text-red-300 font-bold">⚠️ No price data returned from provider. Check data source configuration and network access.</div>
              )}
            </div>
          </div>
          {/* Statistics Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <StatCard
              label="Execution Time"
              value={`${response.execution_time_ms.toFixed(2)}ms`}
              subtitle="C++ accelerated"
              color="purple"
            />
            <StatCard
              label="Simulations"
              value={response.num_simulations.toLocaleString()}
              subtitle={`${response.num_days} days forecast`}
              color="indigo"
            />
            <StatCard
              label="Portfolio Size"
              value={response.tickers.length.toString()}
              subtitle="assets"
              color="blue"
            />
            <StatCard
              label="Status"
              value="Complete"
              subtitle="✓ Ready for analysis"
              color="green"
            />
          </div>

          {/* Portfolio Weights */}
          <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold text-gray-900 dark:text-white mb-4">
              Portfolio Weights ({request.weighting === 'min_var' ? 'Minimum Variance' : 'Equal'})
            </h2>
            <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-5 gap-4">
              {response.portfolio_weights && response.tickers.map((ticker, i) => (
                <div
                  key={ticker}
                  className="p-4 bg-gray-50 dark:bg-gray-700 rounded-lg border border-gray-200 dark:border-gray-600"
                >
                  <div className="text-sm text-gray-600 dark:text-gray-400">
                    {ticker}
                  </div>
                  <div className="text-2xl font-bold text-gray-900 dark:text-white mt-1">
                    {(response.portfolio_weights![i] * 100).toFixed(1)}%
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Simulation Results Info */}
          <div className="bg-gradient-to-br from-purple-50 to-indigo-50 dark:from-purple-900/20 dark:to-indigo-900/20 rounded-lg p-6 border border-purple-200 dark:border-purple-800">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">
              🚀 Simulation Complete!
            </h3>
            <p className="text-gray-700 dark:text-gray-300">
              Generated <strong>{response.num_simulations.toLocaleString()}</strong> Monte Carlo
              paths for a <strong>{response.tickers.length}-asset</strong> portfolio over{' '}
              <strong>{response.num_days} trading days</strong>.
            </p>
            <p className="text-gray-600 dark:text-gray-400 mt-2 text-sm">
              Using Cholesky decomposition for correlated returns and geometric Brownian motion.
              Parallelized across all CPU cores with OpenMP.
            </p>
            <div className="mt-4 text-sm text-purple-700 dark:text-purple-300 font-medium">
              ⚡ C++ Performance: 9-11x faster than pure Python implementation
            </div>
          </div>

          {/* Note about visualization */}
          <div className="bg-blue-50 dark:bg-blue-900/20 border border-blue-200 dark:border-blue-800 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-900 dark:text-blue-100 mb-2">
              📊 Visualization Coming Soon
            </h3>
            <p className="text-blue-800 dark:text-blue-200 mb-3">
              Next step: Integrate Plotly.js or D3.js for interactive visualization:
            </p>
            <ul className="space-y-2 text-blue-700 dark:text-blue-300">
              <li>• <strong>Fan Chart:</strong> Display all {response.num_simulations.toLocaleString()} price paths</li>
              <li>• <strong>Histogram:</strong> Distribution of final portfolio values</li>
              <li>• <strong>Statistics:</strong> Mean, median, VaR, CVaR, percentiles</li>
              <li>• <strong>Confidence Intervals:</strong> 95%, 90%, 80% bands</li>
            </ul>
          </div>
        </div>
      )}
    </div>
  );
}

// Stat Card Component
interface StatCardProps {
  label: string;
  value: string;
  subtitle: string;
  color: 'purple' | 'indigo' | 'blue' | 'green';
}

function StatCard({ label, value, subtitle, color }: StatCardProps) {
  const colorClasses = {
    purple: 'from-purple-500 to-purple-600',
    indigo: 'from-indigo-500 to-indigo-600',
    blue: 'from-blue-500 to-blue-600',
    green: 'from-green-500 to-green-600',
  };

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700">
      <div className="text-sm font-medium text-gray-600 dark:text-gray-400 mb-2">
        {label}
      </div>
      <div className={`text-2xl font-bold bg-gradient-to-r ${colorClasses[color]} bg-clip-text text-transparent`}>
        {value}
      </div>
      <div className="text-xs text-gray-500 dark:text-gray-500 mt-1">
        {subtitle}
      </div>
    </div>
  );
}
