import React, { useState } from 'react';
import DatePicker from 'react-datepicker';
import { Calendar, TrendingUp, AlertCircle, Loader2, Sparkles } from 'lucide-react';
import { statArbApi } from '../services/api';
import type { FindPairsRequest, FindPairsResponse, CointegratedPair, SpreadAnalysisResponse } from '../types/api';
import PairsTable from '../components/PairsTable';
import SpreadChart from '../components/SpreadChart';
import { UNIVERSES } from '../constants/universes';
import 'react-datepicker/dist/react-datepicker.css';
import '../styles/datepicker.css';

const MIN_DATE = new Date('2010-01-01');
const MAX_DATE = new Date();

interface FormData {
  tickers: string;
  startDate: Date;
  endDate: Date;
  pValueThreshold: number;
}

const StatArbAnalysis: React.FC = () => {
  const [selectedUniverse, setSelectedUniverse] = useState<string>('');
  const [formData, setFormData] = useState<FormData>({
    tickers: '',
    startDate: new Date(Date.now() - 365 * 24 * 60 * 60 * 1000), // 1 year ago
    endDate: new Date(),
    pValueThreshold: 0.05,
  });

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [pairsResult, setPairsResult] = useState<FindPairsResponse | null>(null);
  const [selectedPair, setSelectedPair] = useState<CointegratedPair | null>(null);
  const [spreadData, setSpreadData] = useState<SpreadAnalysisResponse | null>(null);
  const [loadingSpread, setLoadingSpread] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setPairsResult(null);
    setSelectedPair(null);
    setSpreadData(null);

    // Parse tickers
    const tickerList = formData.tickers
      .split(',')
      .map(t => t.trim().toUpperCase())
      .filter(t => t.length > 0);

    if (tickerList.length < 2) {
      setError('Please enter at least 2 tickers (comma-separated)');
      return;
    }

    if (formData.startDate >= formData.endDate) {
      setError('Start date must be before end date');
      return;
    }

    setLoading(true);

    try {
      const request: FindPairsRequest = {
        tickers: tickerList,
        start_date: formData.startDate.toISOString().split('T')[0],
        end_date: formData.endDate.toISOString().split('T')[0],
        p_value_threshold: formData.pValueThreshold,
      };

      const result = await statArbApi.findPairs(request);
      setPairsResult(result);

      if (result.cointegrated_count === 0) {
        setError('No cointegrated pairs found. Try different tickers or adjust the p-value threshold.');
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to find pairs');
      console.error('Error finding pairs:', err);
    } finally {
      setLoading(false);
    }
  };

  const handlePairSelect = async (pair: CointegratedPair) => {
    setSelectedPair(pair);
    setLoadingSpread(true);
    setError(null);

    try {
      const result = await statArbApi.analyzeSpread({
        ticker_a: pair.asset_1,
        ticker_b: pair.asset_2,
        start_date: formData.startDate.toISOString().split('T')[0],
        end_date: formData.endDate.toISOString().split('T')[0],
        window: 20,
        entry_threshold: 2.0,
        exit_threshold: 0.0,
      });
      setSpreadData(result);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to analyze spread');
      console.error('Error analyzing spread:', err);
    } finally {
      setLoadingSpread(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-8 px-4">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8 text-center">
          <div className="flex items-center justify-center mb-4">
            <TrendingUp className="w-12 h-12 text-sky-500 mr-3" />
            <h1 className="text-4xl font-bold text-white">Statistical Arbitrage</h1>
          </div>
          <p className="text-slate-400 text-lg">
            Find cointegrated pairs for mean-reversion trading strategies
          </p>
        </div>

        {/* Form Card */}
        <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg shadow-xl p-6 mb-6 border border-slate-700">
          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Helper Box - Quick Start */}
            <div className="bg-gradient-to-r from-sky-900/30 to-teal-900/30 border border-sky-500/30 rounded-lg p-4">
              <div className="flex items-start">
                <Sparkles className="w-5 h-5 text-sky-400 mr-3 mt-0.5 flex-shrink-0" />
                <div className="flex-1">
                  <h3 className="text-sm font-semibold text-sky-400 mb-2">
                    💡 Quick Start: Use Pre-defined Universes
                  </h3>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-2 mb-3">
                    {UNIVERSES.map((universe) => (
                      <button
                        key={universe.id}
                        type="button"
                        onClick={() => {
                          setSelectedUniverse(universe.id);
                          setFormData({ ...formData, tickers: universe.tickers.join(', ') });
                        }}
                        className={`px-3 py-2 rounded-lg text-left text-sm transition-all ${
                          selectedUniverse === universe.id
                            ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/50'
                            : 'bg-slate-700/50 text-slate-300 hover:bg-slate-600/50 border border-slate-600'
                        }`}
                      >
                        <div className="flex items-center">
                          <span className="text-lg mr-2">{universe.icon}</span>
                          <div>
                            <div className="font-medium">
                              {universe.name}
                              {universe.recommended && (
                                <span className="ml-1 text-xs text-amber-400">★</span>
                              )}
                            </div>
                            <div className="text-xs opacity-75">{universe.tickers.length} tickers</div>
                          </div>
                        </div>
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-slate-400">
                    <strong className="text-sky-400">Tip:</strong> Start with "Popular ETFs" (★ recommended) for fastest results. 
                    Or enter your own tickers below.
                  </p>
                </div>
              </div>
            </div>

            {/* Tickers Input */}
            <div>
              <label htmlFor="tickers" className="block text-sm font-medium text-slate-300 mb-2">
                Tickers (comma-separated)
              </label>
              <input
                type="text"
                id="tickers"
                value={formData.tickers}
                onChange={(e) => {
                  setFormData({ ...formData, tickers: e.target.value });
                  setSelectedUniverse(''); // Clear universe selection when manually editing
                }}
                placeholder="e.g., SPY, IVV, VOO, QQQ, VTI, ITOT"
                className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white placeholder-slate-400 focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                required
              />
              <p className="mt-1 text-xs text-slate-400">
                Enter 5-20 tickers for best results. <strong className="text-sky-400">Try ETFs like SPY, IVV, VOO, QQQ, VTI</strong> - they often show cointegration.
              </p>
            </div>

            {/* Date Range */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label htmlFor="startDate" className="block text-sm font-medium text-slate-300 mb-2">
                  Start Date
                </label>
                <div className="relative">
                  <DatePicker
                    selected={formData.startDate}
                    onChange={(date: Date | null) => date && setFormData({ ...formData, startDate: date })}
                    minDate={MIN_DATE}
                    maxDate={formData.endDate}
                    dateFormat="yyyy-MM-dd"
                    showMonthDropdown
                    showYearDropdown
                    dropdownMode="select"
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  />
                  <Calendar className="absolute right-3 top-2.5 w-5 h-5 text-slate-400 pointer-events-none" />
                </div>
              </div>
              <div>
                <label htmlFor="endDate" className="block text-sm font-medium text-slate-300 mb-2">
                  End Date
                </label>
                <div className="relative">
                  <DatePicker
                    selected={formData.endDate}
                    onChange={(date: Date | null) => date && setFormData({ ...formData, endDate: date })}
                    minDate={formData.startDate}
                    maxDate={MAX_DATE}
                    dateFormat="yyyy-MM-dd"
                    showMonthDropdown
                    showYearDropdown
                    dropdownMode="select"
                    className="w-full px-4 py-2 bg-slate-700 border border-slate-600 rounded-lg text-white focus:outline-none focus:ring-2 focus:ring-sky-500 focus:border-transparent"
                  />
                  <Calendar className="absolute right-3 top-2.5 w-5 h-5 text-slate-400 pointer-events-none" />
                </div>
              </div>
            </div>

            {/* P-Value Threshold Slider */}
            <div>
              <label htmlFor="pValueThreshold" className="block text-sm font-medium text-slate-300 mb-2">
                P-Value Threshold: {formData.pValueThreshold.toFixed(2)}
              </label>
              <input
                type="range"
                id="pValueThreshold"
                min="0.01"
                max="0.10"
                step="0.01"
                value={formData.pValueThreshold}
                onChange={(e) => setFormData({ ...formData, pValueThreshold: parseFloat(e.target.value) })}
                className="w-full h-2 bg-slate-700 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-xs text-slate-400 mt-1">
                <span>0.01 (strict)</span>
                <span>0.05 (standard)</span>
                <span>0.10 (lenient)</span>
              </div>
            </div>

            {/* Submit Button */}
            <button
              type="submit"
              disabled={loading}
              className="w-full bg-gradient-to-r from-sky-500 to-teal-500 hover:from-sky-600 hover:to-teal-600 text-white font-semibold py-3 px-6 rounded-lg transition-all duration-200 transform hover:scale-105 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center"
            >
  {loading ? (
                <>
                  <Loader2 className="w-5 h-5 mr-2 animate-spin" />
                  <span>
                    Testing combinations
                    {formData.tickers.split(',').filter(t => t.trim()).length > 0 && (
                      <span className="ml-1 text-sky-200">
                        ({Math.floor((formData.tickers.split(',').filter(t => t.trim()).length * (formData.tickers.split(',').filter(t => t.trim()).length - 1)) / 2)} pairs)
                      </span>
                    )}
                  </span>
                </>
              ) : (
                <>
                  <TrendingUp className="w-5 h-5 mr-2" />
                  Find Cointegrated Pairs
                </>
              )}
            </button>
          </form>
        </div>

        {/* Error Message */}
        {error && (
          <div className="bg-red-900/20 border border-red-500 rounded-lg p-4 mb-6 flex items-start">
            <AlertCircle className="w-5 h-5 text-red-500 mr-3 mt-0.5 flex-shrink-0" />
            <p className="text-red-300">{error}</p>
          </div>
        )}

        {/* Results Section */}
        {pairsResult && (
          <div className="space-y-6">
            {/* Summary Stats */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                <p className="text-slate-400 text-sm mb-1">Total Combinations</p>
                <p className="text-3xl font-bold text-white">{pairsResult.total_combinations_tested}</p>
              </div>
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                <p className="text-slate-400 text-sm mb-1">Cointegrated Pairs</p>
                <p className="text-3xl font-bold text-teal-400">{pairsResult.cointegrated_count}</p>
              </div>
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                <p className="text-slate-400 text-sm mb-1">Success Rate</p>
                <p className="text-3xl font-bold text-amber-400">
                  {((pairsResult.cointegrated_count / pairsResult.total_combinations_tested) * 100).toFixed(1)}%
                </p>
              </div>
            </div>

            {/* Pairs Table or Empty State */}
            {pairsResult.pairs.length > 0 ? (
              <PairsTable
                pairs={pairsResult.pairs}
                selectedPair={selectedPair}
                onPairSelect={handlePairSelect}
              />
            ) : (
              <div className="bg-amber-900/20 border border-amber-500/30 rounded-lg p-6">
                <div className="flex items-start">
                  <AlertCircle className="w-6 h-6 text-amber-400 mr-3 mt-0.5 flex-shrink-0" />
                  <div>
                    <h3 className="text-lg font-semibold text-amber-400 mb-2">
                      No Cointegrated Pairs Found
                    </h3>
                    <p className="text-slate-300 mb-3">
                      No pairs showed statistical cointegration in this period. This is normal - not all assets are cointegrated!
                    </p>
                    <div className="text-sm text-slate-400 space-y-1">
                      <p className="font-medium text-slate-300 mb-2">💡 Try these suggestions:</p>
                      <ul className="list-disc list-inside space-y-1 ml-2">
                        <li><strong className="text-sky-400">Use ETFs that track the same index:</strong> SPY, IVV, VOO (all S&P 500)</li>
                        <li><strong className="text-sky-400">Click "Popular ETFs"</strong> button above - known to have cointegrated pairs</li>
                        <li><strong className="text-teal-400">Extend the date range</strong> to 2-5 years for more stable relationships</li>
                        <li><strong className="text-teal-400">Increase p-value threshold</strong> to 0.10 to be more lenient</li>
                        <li><strong className="text-amber-400">Use more tickers</strong> (10-15) to test more combinations</li>
                      </ul>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Spread Chart */}
            {selectedPair && (
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg p-6 border border-slate-700">
                <h3 className="text-xl font-semibold text-white mb-4">
                  Spread Analysis: {selectedPair.asset_1} / {selectedPair.asset_2}
                </h3>
                {loadingSpread ? (
                  <div className="flex items-center justify-center py-12">
                    <Loader2 className="w-8 h-8 text-sky-500 animate-spin" />
                    <span className="ml-3 text-slate-400">Analyzing spread...</span>
                  </div>
                ) : spreadData ? (
                  <SpreadChart data={spreadData} />
                ) : null}
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default StatArbAnalysis;
