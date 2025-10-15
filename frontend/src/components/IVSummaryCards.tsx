import React from 'react';
import type { IVSurfaceMetrics } from '../types/ivSurface';

interface IVSummaryCardsProps {
  spotPrice: number;
  metrics: IVSurfaceMetrics;
}

const IVSummaryCards: React.FC<IVSummaryCardsProps> = ({ spotPrice, metrics }) => {
  const formatPercent = (value: number | null): string => {
    if (value === null) return 'N/A';
    return `${(value * 100).toFixed(2)}%`;
  };

  const formatNumber = (value: number, decimals: number = 2): string => {
    return value.toFixed(decimals);
  };

  const cards = [
    {
      title: 'Spot Price',
      value: `$${formatNumber(spotPrice, 2)}`,
      subtitle: 'Current Market Price',
      bgColor: 'bg-sky-900/40',
      borderColor: 'border-sky-700',
      textColor: 'text-sky-300',
      valueColor: 'text-sky-100',
      iconBg: 'bg-sky-800/50',
      icon: '📈',
    },
    {
      title: 'ATM IV',
      value: formatPercent(metrics.atm_iv_avg),
      subtitle: `Call: ${formatPercent(metrics.atm_call_iv)} | Put: ${formatPercent(metrics.atm_put_iv)}`,
      bgColor: 'bg-teal-900/40',
      borderColor: 'border-teal-700',
      textColor: 'text-teal-300',
      valueColor: 'text-teal-100',
      iconBg: 'bg-teal-800/50',
      icon: '📊',
    },
    {
      title: 'Put-Call Skew',
      value: formatPercent(metrics.put_call_skew),
      subtitle: 'OTM Put IV - OTM Call IV',
      bgColor: 'bg-amber-900/40',
      borderColor: 'border-amber-700',
      textColor: 'text-amber-300',
      valueColor: 'text-amber-100',
      iconBg: 'bg-amber-800/50',
      icon: '⚖️',
    },
    {
      title: 'Total Contracts',
      value: `${metrics.total_call_contracts + metrics.total_put_contracts}`,
      subtitle: `${metrics.total_call_contracts} Calls | ${metrics.total_put_contracts} Puts`,
      bgColor: 'bg-indigo-900/40',
      borderColor: 'border-indigo-700',
      textColor: 'text-indigo-300',
      valueColor: 'text-indigo-100',
      iconBg: 'bg-indigo-800/50',
      icon: '🎯',
    },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
      {cards.map((card, index) => (
        <div
          key={index}
          className={`${card.bgColor} ${card.borderColor} backdrop-blur-lg border-2 rounded-xl p-6 shadow-xl hover:shadow-2xl hover:scale-105 transition-all duration-300`}
        >
          <div className="flex items-start justify-between mb-3">
            <div className={`${card.iconBg} w-12 h-12 rounded-lg flex items-center justify-center text-2xl backdrop-blur-sm`}>
              {card.icon}
            </div>
          </div>
          <h3 className={`text-sm font-medium ${card.textColor} mb-1`}>{card.title}</h3>
          <p className={`text-3xl font-bold ${card.valueColor} mb-2`}>{card.value}</p>
          <p className={`text-xs ${card.textColor} opacity-80`}>{card.subtitle}</p>
        </div>
      ))}
    </div>
  );
};

export default IVSummaryCards;
