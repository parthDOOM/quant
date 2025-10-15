import { useState } from 'react';
import { Play, AlertCircle, Calendar } from 'lucide-react';
import DatePicker from 'react-datepicker';
import 'react-datepicker/dist/react-datepicker.css';
import '../styles/datepicker.css';
import { hrpApi } from '../services/api';
import type { HRPRequest, AnalysisState } from '../types/api';
import { cn } from '../utils/cn';
import Dendrogram from '../components/Dendrogram';
import Heatmap from '../components/Heatmap';
import MultiTickerSelect from '../components/MultiTickerSelect';

type LinkageMethod = 'ward' | 'single' | 'complete' | 'average';

// Yahoo Finance data availability constraints
const MIN_DATE = new Date('2000-01-01'); // yfinance generally has data from 2000 onwards
const MAX_DATE = new Date(); // Today's date

export default function HRPAnalysis() {
  const [state, setState] = useState<AnalysisState>({
    loading: false,
    error: null,
    data: null,
  });

  const [formData, setFormData] = useState<{
    tickers: string[];
    startDate: Date;
    endDate: Date;
    linkageMethod: LinkageMethod;
  }>({
    tickers: ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'NVDA', 'TSLA', 'JPM', 'V', 'WMT'],
    startDate: new Date('2023-01-01'),
    endDate: new Date('2024-12-31'),
    linkageMethod: 'ward',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    // Validation
    if (formData.tickers.length < 2) {
      setState({
        loading: false,
        error: 'Please select at least 2 tickers for analysis',
        data: null,
      });
      return;
    }

    setState({ loading: true, error: null, data: null });

    try {
      const request: HRPRequest = {
        tickers: formData.tickers,
        start_date: formData.startDate.toISOString().split('T')[0],
        end_date: formData.endDate.toISOString().split('T')[0],
        linkage_method: formData.linkageMethod,
      };

      const response = await hrpApi.analyzeHRP(request);
      setState({ loading: false, error: null, data: response });
    } catch (error) {
      setState({
        loading: false,
        error: error instanceof Error ? error.message : 'An error occurred',
        data: null,
      });
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-3xl font-bold text-white mb-2">
          Hierarchical Risk Parity Analysis
        </h1>
        <p className="text-slate-400">
          Optimize your portfolio using clustering-based risk allocation
        </p>
      </div>

      {/* Input Form */}
      <div className="rounded-xl bg-slate-800/50 border border-slate-700 p-6">
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Tickers Input */}
          <div className="relative z-40">
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Portfolio Tickers
            </label>
            <MultiTickerSelect
              selectedTickers={formData.tickers}
              onChange={(tickers) => setFormData({ ...formData, tickers })}
              disabled={state.loading}
              maxSelections={20}
            />
            <p className="mt-1.5 text-xs text-slate-500">
              Search and select ticker symbols (minimum 2, maximum 20)
            </p>
          </div>

          {/* Date Range */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                Start Date
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 pointer-events-none z-10" />
                <DatePicker
                  selected={formData.startDate}
                  onChange={(date: Date | null) =>
                    date && setFormData({ ...formData, startDate: date })
                  }
                  minDate={MIN_DATE}
                  maxDate={formData.endDate}
                  disabled={state.loading}
                  dateFormat="yyyy-MM-dd"
                  className="w-full pl-11 pr-4 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all cursor-pointer"
                  calendarClassName="custom-calendar"
                  showMonthDropdown
                  showYearDropdown
                  dropdownMode="select"
                  placeholderText="Select start date"
                />
              </div>
              <p className="mt-1.5 text-xs text-slate-500">
                Available: Jan 2000 - {new Date().toLocaleDateString('en-US', { month: 'short', year: 'numeric' })}
              </p>
            </div>
            <div>
              <label className="block text-sm font-medium text-slate-300 mb-2">
                End Date
              </label>
              <div className="relative">
                <Calendar className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-slate-500 pointer-events-none z-10" />
                <DatePicker
                  selected={formData.endDate}
                  onChange={(date: Date | null) =>
                    date && setFormData({ ...formData, endDate: date })
                  }
                  minDate={formData.startDate}
                  maxDate={MAX_DATE}
                  disabled={state.loading}
                  dateFormat="yyyy-MM-dd"
                  className="w-full pl-11 pr-4 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all cursor-pointer"
                  calendarClassName="custom-calendar"
                  showMonthDropdown
                  showYearDropdown
                  dropdownMode="select"
                  placeholderText="Select end date"
                />
              </div>
              <p className="mt-1.5 text-xs text-slate-500">
                Must be after start date, up to today
              </p>
            </div>
          </div>

          {/* Linkage Method */}
          <div>
            <label className="block text-sm font-medium text-slate-300 mb-2">
              Linkage Method
            </label>
            <select
              value={formData.linkageMethod}
              onChange={(e) =>
                setFormData({
                  ...formData,
                  linkageMethod: e.target.value as LinkageMethod,
                })
              }
              className="w-full px-4 py-2.5 rounded-lg bg-slate-900 border border-slate-700 text-white focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent transition-all"
              disabled={state.loading}
            >
              <option value="ward">Ward (variance minimization)</option>
              <option value="single">Single (minimum distance)</option>
              <option value="complete">Complete (maximum distance)</option>
              <option value="average">Average (mean distance)</option>
            </select>
            <p className="mt-1.5 text-xs text-slate-500">
              Clustering algorithm for hierarchical grouping
            </p>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={state.loading}
            className={cn(
              'w-full flex items-center justify-center px-6 py-3 rounded-lg font-medium transition-all',
              state.loading
                ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                : 'bg-primary-500 text-white hover:bg-primary-600 hover:shadow-lg hover:shadow-primary-500/50'
            )}
          >
            {state.loading ? (
              <>
                <div className="w-5 h-5 border-2 border-slate-400 border-t-transparent rounded-full animate-spin mr-2"></div>
                Analyzing...
              </>
            ) : (
              <>
                <Play className="w-5 h-5 mr-2" />
                Run Analysis
              </>
            )}
          </button>
        </form>
      </div>

      {/* Error Display */}
      {state.error && (
        <div className="rounded-xl bg-red-500/10 border border-red-500/50 p-4">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-red-400 flex-shrink-0 mt-0.5" />
            <div>
              <h3 className="text-sm font-medium text-red-400 mb-1">
                Analysis Failed
              </h3>
              <p className="text-sm text-red-300">{state.error}</p>
            </div>
          </div>
        </div>
      )}

      {/* Results Display */}
      {state.data && (
        <div className="space-y-6">
          {/* Summary Cards */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700 hover:border-primary-500 transition-colors">
              <div className="text-sm text-slate-400 mb-1">Tickers Analyzed</div>
              <div className="text-2xl font-bold text-white">
                {state.data.ordered_tickers.length}
              </div>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700 hover:border-primary-500 transition-colors">
              <div className="text-sm text-slate-400 mb-1">Data Points</div>
              <div className="text-2xl font-bold text-white">
                {state.data.data_points}
              </div>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700 hover:border-primary-500 transition-colors">
              <div className="text-sm text-slate-400 mb-1">Clusters Found</div>
              <div className="text-2xl font-bold text-primary-400">
                {Object.keys(state.data.cluster_leaf_map).length}
              </div>
            </div>
            <div className="p-4 rounded-lg bg-slate-800/50 border border-slate-700 hover:border-primary-500 transition-colors">
              <div className="text-sm text-slate-400 mb-1">Linkage Method</div>
              <div className="text-2xl font-bold text-white capitalize">
                {state.data.linkage_method}
              </div>
            </div>
          </div>

          {/* Ordered Tickers */}
          <div className="rounded-xl bg-slate-800/50 border border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Hierarchical Ordering
            </h3>
            <div className="flex flex-wrap gap-2">
              {state.data.ordered_tickers.map((ticker, index) => (
                <div
                  key={ticker}
                  className="px-3 py-1.5 rounded-lg bg-primary-500/20 border border-primary-500/50 text-primary-300 text-sm font-medium"
                >
                  {index + 1}. {ticker}
                </div>
              ))}
            </div>
          </div>

          {/* Dendrogram Visualization */}
          <div className="rounded-xl bg-slate-800/50 border border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Dendrogram Visualization
            </h3>
            <Dendrogram
              data={state.data.dendrogram_data}
              width={1000}
              height={600}
            />
          </div>

          <div className="rounded-xl bg-slate-800/50 border border-slate-700 p-6">
            <h3 className="text-lg font-semibold text-white mb-4">
              Correlation Heatmap
            </h3>
            <Heatmap
              data={state.data.heatmap_data}
              tickers={state.data.ordered_tickers}
              width={1000}
              height={1000}
            />
          </div>
        </div>
      )}
    </div>
  );
}
