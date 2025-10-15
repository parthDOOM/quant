import React, { useState, useMemo } from 'react';
import type { OptionContractIV } from '../types/ivSurface';

interface IVDataTableProps {
  calls: OptionContractIV[];
  puts: OptionContractIV[];
}

type SortField = 'strike' | 'moneyness' | 'time_to_expiry' | 'implied_volatility' | 'volume';
type SortDirection = 'asc' | 'desc';

const IVDataTable: React.FC<IVDataTableProps> = ({ calls, puts }) => {
  const [activeTab, setActiveTab] = useState<'calls' | 'puts'>('calls');
  const [sortField, setSortField] = useState<SortField>('strike');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const currentData = activeTab === 'calls' ? calls : puts;

  const sortedData = useMemo(() => {
    const data = [...currentData];
    data.sort((a, b) => {
      const aVal = a[sortField];
      const bVal = b[sortField];

      // Handle null IVs
      if (sortField === 'implied_volatility') {
        if (aVal === null && bVal === null) return 0;
        if (aVal === null) return 1;
        if (bVal === null) return -1;
      }

      // Type guard: at this point, for implied_volatility, both are non-null
      if (aVal === null || bVal === null) return 0;
      
      if (aVal < bVal) return sortDirection === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
    return data;
  }, [currentData, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('asc');
    }
  };

  const getIVColor = (iv: number | null): string => {
    if (iv === null) return 'text-slate-500';
    if (iv < 0.2) return 'text-blue-400';
    if (iv < 0.4) return 'text-green-400';
    if (iv < 0.6) return 'text-yellow-400';
    if (iv < 0.8) return 'text-orange-400';
    return 'text-red-400';
  };

  const formatPercent = (value: number | null): string => {
    if (value === null) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatNumber = (value: number, decimals: number = 2): string => {
    return value.toFixed(decimals);
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <span className="text-gray-300">⇅</span>;
    return sortDirection === 'asc' ? <span>↑</span> : <span>↓</span>;
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl shadow-xl border border-slate-700">
      {/* Tabs */}
      <div className="flex border-b border-slate-700">
        <button
          onClick={() => setActiveTab('calls')}
          className={`flex-1 px-6 py-4 text-sm font-semibold transition-colors ${
            activeTab === 'calls'
              ? 'text-teal-400 border-b-2 border-teal-500 bg-teal-900/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
          }`}
        >
          Calls ({calls.length})
        </button>
        <button
          onClick={() => setActiveTab('puts')}
          className={`flex-1 px-6 py-4 text-sm font-semibold transition-colors ${
            activeTab === 'puts'
              ? 'text-amber-400 border-b-2 border-amber-500 bg-amber-900/30'
              : 'text-slate-400 hover:text-slate-200 hover:bg-slate-700/50'
          }`}
        >
          Puts ({puts.length})
        </button>
      </div>

      {/* Table */}
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead className="bg-slate-900/50 border-b border-slate-700">
            <tr>
              <th
                onClick={() => handleSort('strike')}
                className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider cursor-pointer hover:bg-slate-700/50"
              >
                Strike <SortIcon field="strike" />
              </th>
              <th
                onClick={() => handleSort('moneyness')}
                className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider cursor-pointer hover:bg-slate-700/50"
              >
                Moneyness <SortIcon field="moneyness" />
              </th>
              <th
                onClick={() => handleSort('time_to_expiry')}
                className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider cursor-pointer hover:bg-slate-700/50"
              >
                Time (Years) <SortIcon field="time_to_expiry" />
              </th>
              <th
                onClick={() => handleSort('implied_volatility')}
                className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider cursor-pointer hover:bg-slate-700/50"
              >
                IV <SortIcon field="implied_volatility" />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Bid
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Ask
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Mid
              </th>
              <th
                onClick={() => handleSort('volume')}
                className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider cursor-pointer hover:bg-slate-700/50"
              >
                Volume <SortIcon field="volume" />
              </th>
              <th className="px-6 py-3 text-left text-xs font-medium text-slate-400 uppercase tracking-wider">
                Expiration
              </th>
            </tr>
          </thead>
          <tbody className="bg-slate-800/30 divide-y divide-slate-700">
            {sortedData.length === 0 ? (
              <tr>
                <td colSpan={9} className="px-6 py-8 text-center text-slate-400">
                  No contracts available with current filters
                </td>
              </tr>
            ) : (
              sortedData.map((contract, index) => (
                <tr
                  key={index}
                  className="hover:bg-slate-700/30 transition-colors"
                >
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-white">
                    ${formatNumber(contract.strike, 2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                    {formatNumber(contract.moneyness, 3)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                    {formatNumber(contract.time_to_expiry, 3)}
                  </td>
                  <td
                    className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${getIVColor(
                      contract.implied_volatility
                    )}`}
                  >
                    {formatPercent(contract.implied_volatility)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                    ${formatNumber(contract.bid, 2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                    ${formatNumber(contract.ask, 2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                    ${formatNumber(contract.mid_price, 2)}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-300">
                    {contract.volume.toLocaleString()}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-slate-400">
                    {contract.expiration}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

      {/* Footer with stats */}
      <div className="px-6 py-4 bg-slate-900/50 border-t border-slate-700 text-xs text-slate-400">
        <div className="flex justify-between items-center">
          <span>
            Showing {sortedData.length} contracts
            {sortedData.length > 0 && (
              <>
                {' '}
                | IV Range: {formatPercent(sortedData.filter((c) => c.implied_volatility !== null)[0]?.implied_volatility)}{' '}
                - {formatPercent(sortedData.filter((c) => c.implied_volatility !== null).slice(-1)[0]?.implied_volatility)}
              </>
            )}
          </span>
          <span className="text-slate-500">
            💡 Tip: Click column headers to sort
          </span>
        </div>
      </div>
    </div>
  );
};

export default IVDataTable;
