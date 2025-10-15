import React, { useState } from 'react';
import { ArrowUpDown, ArrowUp, ArrowDown } from 'lucide-react';
import type { CointegratedPair } from '../types/api';

interface PairsTableProps {
  pairs: CointegratedPair[];
  selectedPair: CointegratedPair | null;
  onPairSelect: (pair: CointegratedPair) => void;
}

type SortColumn = 'p_value' | 'hedge_ratio' | 'half_life' | 'correlation';
type SortDirection = 'asc' | 'desc';

const PairsTable: React.FC<PairsTableProps> = ({ pairs, selectedPair, onPairSelect }) => {
  const [sortColumn, setSortColumn] = useState<SortColumn>('p_value');
  const [sortDirection, setSortDirection] = useState<SortDirection>('asc');

  const handleSort = (column: SortColumn) => {
    if (sortColumn === column) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortColumn(column);
      setSortDirection('asc');
    }
  };

  const sortedPairs = [...pairs].sort((a, b) => {
    const aValue = a[sortColumn];
    const bValue = b[sortColumn];
    const multiplier = sortDirection === 'asc' ? 1 : -1;
    return (aValue - bValue) * multiplier;
  });

  const getPValueBadge = (pValue: number) => {
    if (pValue < 0.01) {
      return (
        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-green-900/30 text-green-400 border border-green-500/30">
          Highly Significant
        </span>
      );
    } else if (pValue < 0.05) {
      return (
        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-yellow-900/30 text-yellow-400 border border-yellow-500/30">
          Significant
        </span>
      );
    } else {
      return (
        <span className="px-2 py-1 text-xs font-semibold rounded-full bg-slate-700/30 text-slate-400 border border-slate-500/30">
          Marginal
        </span>
      );
    }
  };

  const SortIcon: React.FC<{ column: SortColumn }> = ({ column }) => {
    if (sortColumn !== column) {
      return <ArrowUpDown className="w-4 h-4 text-slate-500" />;
    }
    return sortDirection === 'asc' ? (
      <ArrowUp className="w-4 h-4 text-sky-400" />
    ) : (
      <ArrowDown className="w-4 h-4 text-sky-400" />
    );
  };

  return (
    <div className="bg-slate-800/50 backdrop-blur-sm rounded-lg border border-slate-700 overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="border-b border-slate-700 bg-slate-900/50">
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Pair
              </th>
              <th
                className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider cursor-pointer hover:text-sky-400 transition-colors"
                onClick={() => handleSort('p_value')}
              >
                <div className="flex items-center space-x-2">
                  <span>P-Value</span>
                  <SortIcon column="p_value" />
                </div>
              </th>
              <th className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider">
                Significance
              </th>
              <th
                className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider cursor-pointer hover:text-sky-400 transition-colors"
                onClick={() => handleSort('hedge_ratio')}
              >
                <div className="flex items-center space-x-2">
                  <span>Hedge Ratio</span>
                  <SortIcon column="hedge_ratio" />
                </div>
              </th>
              <th
                className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider cursor-pointer hover:text-sky-400 transition-colors"
                onClick={() => handleSort('half_life')}
              >
                <div className="flex items-center space-x-2">
                  <span>Half-Life (days)</span>
                  <SortIcon column="half_life" />
                </div>
              </th>
              <th
                className="px-6 py-4 text-left text-xs font-semibold text-slate-300 uppercase tracking-wider cursor-pointer hover:text-sky-400 transition-colors"
                onClick={() => handleSort('correlation')}
              >
                <div className="flex items-center space-x-2">
                  <span>Correlation</span>
                  <SortIcon column="correlation" />
                </div>
              </th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-700">
            {sortedPairs.map((pair, index) => {
              const isSelected =
                selectedPair &&
                selectedPair.asset_1 === pair.asset_1 &&
                selectedPair.asset_2 === pair.asset_2;

              return (
                <tr
                  key={`${pair.asset_1}-${pair.asset_2}-${index}`}
                  onClick={() => onPairSelect(pair)}
                  className={`cursor-pointer transition-colors ${
                    isSelected
                      ? 'bg-sky-900/30 border-l-4 border-l-sky-500'
                      : 'hover:bg-slate-700/30'
                  }`}
                >
                  <td className="px-6 py-4 whitespace-nowrap">
                    <div className="flex items-center space-x-2">
                      <span className="font-semibold text-white">{pair.asset_1}</span>
                      <span className="text-slate-500">/</span>
                      <span className="font-semibold text-white">{pair.asset_2}</span>
                    </div>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-slate-300 font-mono text-sm">
                      {pair.p_value.toFixed(4)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">{getPValueBadge(pair.p_value)}</td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-slate-300 font-mono text-sm">
                      {pair.hedge_ratio.toFixed(4)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-slate-300 font-mono text-sm">
                      {pair.half_life.toFixed(1)}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap">
                    <span className="text-slate-300 font-mono text-sm">
                      {pair.correlation.toFixed(3)}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* Empty State */}
      {pairs.length === 0 && (
        <div className="py-12 text-center">
          <p className="text-slate-400 text-lg">No cointegrated pairs found</p>
          <p className="text-slate-500 text-sm mt-2">
            Try adjusting the p-value threshold or using different tickers
          </p>
        </div>
      )}
    </div>
  );
};

export default PairsTable;
