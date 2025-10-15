import React, { useState, useRef, useEffect } from 'react';
import { Search, TrendingUp } from 'lucide-react';

interface TickerOption {
  symbol: string;
  name: string;
  category?: string;
}

interface TickerAutocompleteProps {
  value: string;
  onChange: (value: string) => void;
  onSelect: (ticker: string) => void;
  disabled?: boolean;
}

// Popular tickers with options activity
const POPULAR_TICKERS: TickerOption[] = [
  // Tech Giants
  { symbol: 'AAPL', name: 'Apple Inc.', category: 'Tech' },
  { symbol: 'MSFT', name: 'Microsoft Corp.', category: 'Tech' },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', category: 'Tech' },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', category: 'Tech' },
  { symbol: 'META', name: 'Meta Platforms Inc.', category: 'Tech' },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', category: 'Tech' },
  { symbol: 'TSLA', name: 'Tesla Inc.', category: 'Auto' },
  
  // Finance
  { symbol: 'JPM', name: 'JPMorgan Chase', category: 'Finance' },
  { symbol: 'BAC', name: 'Bank of America', category: 'Finance' },
  { symbol: 'GS', name: 'Goldman Sachs', category: 'Finance' },
  { symbol: 'MS', name: 'Morgan Stanley', category: 'Finance' },
  
  // Indices & ETFs
  { symbol: 'SPY', name: 'S&P 500 ETF', category: 'ETF' },
  { symbol: 'QQQ', name: 'Nasdaq 100 ETF', category: 'ETF' },
  { symbol: 'IWM', name: 'Russell 2000 ETF', category: 'ETF' },
  { symbol: 'DIA', name: 'Dow Jones ETF', category: 'ETF' },
  { symbol: 'VIX', name: 'Volatility Index', category: 'Index' },
  
  // Other Popular
  { symbol: 'AMD', name: 'Advanced Micro Devices', category: 'Tech' },
  { symbol: 'NFLX', name: 'Netflix Inc.', category: 'Media' },
  { symbol: 'DIS', name: 'Walt Disney Co.', category: 'Media' },
  { symbol: 'BA', name: 'Boeing Co.', category: 'Aerospace' },
  { symbol: 'GM', name: 'General Motors', category: 'Auto' },
  { symbol: 'F', name: 'Ford Motor Co.', category: 'Auto' },
  { symbol: 'XOM', name: 'Exxon Mobil', category: 'Energy' },
  { symbol: 'CVX', name: 'Chevron Corp.', category: 'Energy' },
  { symbol: 'WMT', name: 'Walmart Inc.', category: 'Retail' },
  { symbol: 'COST', name: 'Costco Wholesale', category: 'Retail' },
];

const TickerAutocomplete: React.FC<TickerAutocompleteProps> = ({
  value,
  onChange,
  onSelect,
  disabled = false,
}) => {
  const [showDropdown, setShowDropdown] = useState(false);
  const [filteredTickers, setFilteredTickers] = useState<TickerOption[]>([]);
  const [selectedIndex, setSelectedIndex] = useState<number>(-1);
  const inputRef = useRef<HTMLInputElement>(null);
  const dropdownRef = useRef<HTMLDivElement>(null);

  // Filter tickers based on input
  useEffect(() => {
    if (value.length > 0) {
      const searchTerm = value.toUpperCase();
      const filtered = POPULAR_TICKERS.filter(
        (ticker) =>
          ticker.symbol.startsWith(searchTerm) ||
          ticker.name.toUpperCase().includes(searchTerm)
      );
      setFilteredTickers(filtered);
      setShowDropdown(filtered.length > 0);
      setSelectedIndex(-1);
    } else {
      // Show popular tickers when empty
      setFilteredTickers(POPULAR_TICKERS.slice(0, 10));
      setShowDropdown(false);
    }
  }, [value]);

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

  const handleInputChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newValue = e.target.value.toUpperCase();
    onChange(newValue);
  };

  const handleSelectTicker = (symbol: string) => {
    onChange(symbol);
    onSelect(symbol);
    setShowDropdown(false);
    inputRef.current?.blur();
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (!showDropdown) {
      if (e.key === 'ArrowDown') {
        setShowDropdown(true);
        setSelectedIndex(0);
        e.preventDefault();
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
          handleSelectTicker(filteredTickers[selectedIndex].symbol);
        } else if (value.trim()) {
          onSelect(value.trim());
          setShowDropdown(false);
        }
        break;
      case 'Escape':
        setShowDropdown(false);
        setSelectedIndex(-1);
        break;
    }
  };

  const handleFocus = () => {
    if (value.length === 0) {
      setFilteredTickers(POPULAR_TICKERS.slice(0, 10));
    }
    setShowDropdown(true);
  };

  return (
    <div className="relative">
      <div className="relative">
        <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-slate-400 w-4 h-4" />
        <input
          ref={inputRef}
          type="text"
          value={value}
          onChange={handleInputChange}
          onKeyDown={handleKeyDown}
          onFocus={handleFocus}
          placeholder="Search ticker..."
          className="w-full pl-10 pr-4 py-2 bg-slate-900/50 border border-slate-600 text-white placeholder-slate-500 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent uppercase transition-all"
          disabled={disabled}
        />
      </div>

      {/* Dropdown */}
      {showDropdown && filteredTickers.length > 0 && (
        <div
          ref={dropdownRef}
          className="absolute z-50 w-full mt-2 bg-slate-800 border border-slate-700 rounded-lg shadow-2xl max-h-80 overflow-y-auto custom-scrollbar"
          style={{
            scrollbarWidth: 'thin',
            scrollbarColor: 'rgba(100, 116, 139, 0.6) rgba(30, 41, 59, 0.5)',
          }}
        >
          {/* Header */}
          {value.length === 0 && (
            <div className="px-4 py-2 border-b border-slate-700 flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-teal-400" />
              <span className="text-xs font-medium text-slate-400">
                Popular Tickers
              </span>
            </div>
          )}

          {/* Ticker List */}
          <div className="py-1">
            {filteredTickers.map((ticker, index) => (
              <button
                key={ticker.symbol}
                onClick={() => handleSelectTicker(ticker.symbol)}
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
            <kbd className="px-1.5 py-0.5 bg-slate-700/50 rounded">Enter</kbd> Select •{' '}
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

export default TickerAutocomplete;
