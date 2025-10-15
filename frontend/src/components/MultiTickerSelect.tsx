import React, { useState, useRef, useEffect } from 'react';
import { Search, X, TrendingUp } from 'lucide-react';

interface TickerOption {
  symbol: string;
  name: string;
  category?: string;
}

interface MultiTickerSelectProps {
  selectedTickers: string[];
  onChange: (tickers: string[]) => void;
  disabled?: boolean;
  maxSelections?: number;
}

// Popular tickers with options/portfolio activity
const POPULAR_TICKERS: TickerOption[] = [
  // Tech Giants
  { symbol: 'AAPL', name: 'Apple Inc.', category: 'Tech' },
  { symbol: 'MSFT', name: 'Microsoft Corp.', category: 'Tech' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', category: 'Tech' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', category: 'Tech' },
  { symbol: 'META', name: 'Meta Platforms Inc.', category: 'Tech' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', category: 'Tech' },
  { symbol: 'TSLA', name: 'Tesla Inc.', category: 'Auto' },
  { symbol: 'AMD', name: 'Advanced Micro Devices', category: 'Tech' },
  { symbol: 'NFLX', name: 'Netflix Inc.', category: 'Media' },
  
  // Finance
  { symbol: 'JPM', name: 'JPMorgan Chase', category: 'Finance' },
  { symbol: 'BAC', name: 'Bank of America', category: 'Finance' },
  { symbol: 'GS', name: 'Goldman Sachs', category: 'Finance' },
  { symbol: 'MS', name: 'Morgan Stanley', category: 'Finance' },
  { symbol: 'V', name: 'Visa Inc.', category: 'Finance' },
  { symbol: 'MA', name: 'Mastercard Inc.', category: 'Finance' },
  
  // ETFs
  { symbol: 'SPY', name: 'S&P 500 ETF', category: 'ETF' },
  { symbol: 'QQQ', name: 'Nasdaq 100 ETF', category: 'ETF' },
  { symbol: 'IWM', name: 'Russell 2000 ETF', category: 'ETF' },
  { symbol: 'DIA', name: 'Dow Jones ETF', category: 'ETF' },
  { symbol: 'VTI', name: 'Total Stock Market ETF', category: 'ETF' },
  
  // Consumer & Retail
  { symbol: 'WMT', name: 'Walmart Inc.', category: 'Retail' },
  { symbol: 'COST', name: 'Costco Wholesale', category: 'Retail' },
  { symbol: 'HD', name: 'Home Depot', category: 'Retail' },
  { symbol: 'NKE', name: 'Nike Inc.', category: 'Consumer' },
  { symbol: 'MCD', name: 'McDonalds Corp.', category: 'Consumer' },
  
  // Healthcare
  { symbol: 'UNH', name: 'UnitedHealth Group', category: 'Healthcare' },
  { symbol: 'JNJ', name: 'Johnson & Johnson', category: 'Healthcare' },
  { symbol: 'PFE', name: 'Pfizer Inc.', category: 'Healthcare' },
  
  // Energy
  { symbol: 'XOM', name: 'Exxon Mobil', category: 'Energy' },
  { symbol: 'CVX', name: 'Chevron Corp.', category: 'Energy' },
  
  // Industrial
  { symbol: 'BA', name: 'Boeing Co.', category: 'Aerospace' },
  { symbol: 'CAT', name: 'Caterpillar Inc.', category: 'Industrial' },
  
  // Auto
  { symbol: 'GM', name: 'General Motors', category: 'Auto' },
  { symbol: 'F', name: 'Ford Motor Co.', category: 'Auto' },
];

const MultiTickerSelect: React.FC<MultiTickerSelectProps> = ({
  selectedTickers,
  onChange,
  disabled = false,
  maxSelections = 20,
}) => {
  const [inputValue, setInputValue] = useState('');
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredTickers, setFilteredTickers] = useState<TickerOption[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter tickers based on input and exclude already selected
  useEffect(() => {
    const available = POPULAR_TICKERS.filter(
      (ticker) => !selectedTickers.includes(ticker.symbol)
    );

    if (inputValue.length > 0) {
      const searchTerm = inputValue.toUpperCase();
      const filtered = available.filter(
        (ticker) =>
          ticker.symbol.startsWith(searchTerm) ||
          ticker.name.toUpperCase().includes(searchTerm)
      );
      setFilteredTickers(filtered);
      setShowDropdown(filtered.length > 0);
      setSelectedIndex(-1);
    } else {
      // Show available popular tickers
      setFilteredTickers(available.slice(0, 15));
      setShowDropdown(false);
    }
  }, [inputValue, selectedTickers]);

  // Handle click outside
  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (
        dropdownRef.current &&
        !dropdownRef.current.contains(event.target as Node) &&
        inputRef.current &&
        !inputRef.current.contains(event.target as Node)
      ) {
        setShowDropdown(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleAddTicker = (symbol: string) => {
    if (!selectedTickers.includes(symbol) && selectedTickers.length < maxSelections) {
      onChange([...selectedTickers, symbol]);
      setInputValue('');
      setShowDropdown(false);
      inputRef.current?.focus();
    }
  };

  const handleRemoveTicker = (symbol: string) => {
    onChange(selectedTickers.filter((t) => t !== symbol));
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showDropdown) {
      if (e.key === 'ArrowDown') {
        setShowDropdown(true);
        setSelectedIndex(0);
        e.preventDefault();
      } else if (e.key === 'Backspace' && !inputValue && selectedTickers.length > 0) {
        // Remove last ticker on backspace when input is empty
        onChange(selectedTickers.slice(0, -1));
      }
      return;
    }

    switch (e.key) {
      case 'ArrowDown':
        e.preventDefault();
        setSelectedIndex((prev) =>
          prev < filteredTickers.length - 1 ? prev + 1 : prev
        );
        break;
      case 'ArrowUp':
        e.preventDefault();
        setSelectedIndex((prev) => (prev > 0 ? prev - 1 : -1));
        break;
      case 'Enter':
        e.preventDefault();
        if (selectedIndex >= 0 && selectedIndex < filteredTickers.length) {
          handleAddTicker(filteredTickers[selectedIndex].symbol);
        } else if (inputValue.trim()) {
          // Allow custom ticker input
          const customTicker = inputValue.trim().toUpperCase();
          if (customTicker.length <= 5) {
            handleAddTicker(customTicker);
          }
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const handleFocus = () => {
    if (inputValue.length === 0) {
      const available = POPULAR_TICKERS.filter(
        (ticker) => !selectedTickers.includes(ticker.symbol)
      );
      setFilteredTickers(available.slice(0, 15));
    }
    setShowDropdown(true);
  };

  const atMaxSelections = selectedTickers.length >= maxSelections;

  return (
    <div className="relative">
      {/* Selected Tickers Pills */}
      {selectedTickers.length > 0 && (
        <div className="flex flex-wrap gap-2 mb-3 p-3 bg-slate-900/50 border border-slate-700 rounded-lg">
          {selectedTickers.map((ticker) => (
            <div
              key={ticker}
              className="flex items-center gap-1.5 px-3 py-1.5 bg-teal-500/20 border border-teal-500/30 text-teal-300 rounded-lg text-sm font-medium group hover:bg-teal-500/30 transition-colors"
            >
              <span className="font-mono">{ticker}</span>
              <button
                type="button"
                onClick={() => handleRemoveTicker(ticker)}
                disabled={disabled}
                className="hover:text-teal-100 transition-colors disabled:opacity-50"
              >
                <X className="w-3.5 h-3.5" />
              </button>
            </div>
          ))}
          <div className="flex items-center px-2 text-xs text-slate-500">
            {selectedTickers.length} / {maxSelections} selected
          </div>
        </div>
      )}

      {/* Input */}
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
        <input
          ref={inputRef}
          type="text"
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder={
            atMaxSelections
              ? `Maximum ${maxSelections} tickers reached`
              : selectedTickers.length === 0
              ? 'Search and add tickers...'
              : 'Add more tickers...'
          }
          className="w-full pl-10 pr-4 py-2.5 bg-slate-900/50 border border-slate-600 text-white placeholder-slate-500 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent uppercase transition-all disabled:opacity-50 disabled:cursor-not-allowed"
          disabled={disabled || atMaxSelections}
        />
      </div>

      {/* Dropdown */}
      {showDropdown && filteredTickers.length > 0 && !atMaxSelections && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-2 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl max-h-80 overflow-y-auto custom-scrollbar"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: 'rgba(100, 116, 139, 0.6) rgba(30, 41, 59, 0.5)',
          }}
        >
          {/* Header */}
          {inputValue.length === 0 && (
            <div className="px-4 py-2 border-b border-slate-700 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-teal-400" />
              <span className="text-xs font-medium text-slate-400">
                Available Tickers
              </span>
            </div>
          )}

          {/* Ticker List */}
          <div className="py-1">
            {filteredTickers.map((ticker, index) => (
              <button
                key={ticker.symbol}
                type="button"
                onClick={() => handleAddTicker(ticker.symbol)}
                className={`w-full px-4 py-2.5 text-left transition-colors flex items-center justify-between gap-3 ${
                  index === selectedIndex
                    ? 'bg-teal-500/20 border-l-2 border-teal-400'
                    : 'hover:bg-slate-700/50'
                }`}
              >
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className="font-mono font-semibold text-white">
                      {ticker.symbol}
                    </span>
                    {ticker.category && (
                      <span className="text-xs px-1.5 py-0.5 bg-slate-700/50 text-slate-400 rounded">
                        {ticker.category}
                      </span>
                    )}
                  </div>
                  <div className="text-xs text-slate-400 truncate mt-0.5">
                    {ticker.name}
                  </div>
                </div>
              </button>
            ))}
          </div>

          {/* Footer hint */}
          <div className="px-4 py-2 border-t border-slate-700 text-xs text-slate-500">
            <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded">↑↓</kbd> Navigate •{' '}
            <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded">Enter</kbd> Add •{' '}
            <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded">Esc</kbd> Close
          </div>
        </div>
      )}

      {/* Custom Scrollbar Styles */}
      <style>{`
        .custom-scrollbar::-webkit-scrollbar {
          width: 8px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-track {
          background: rgba(30, 41, 59, 0.5);
          border-radius: 4px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb {
          background: rgba(100, 116, 139, 0.6);
          border-radius: 4px;
        }
        
        .custom-scrollbar::-webkit-scrollbar-thumb:hover {
          background: rgba(148, 163, 184, 0.8);
        }
      `}</style>
    </div>
  );
};

export default MultiTickerSelect;
