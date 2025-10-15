/**
 * Pre-defined ticker universes for statistical arbitrage analysis.
 * These universes contain tickers that are likely to have cointegrated pairs.
 */

export interface Universe {
  id: string;
  name: string;
  description: string;
  tickers: string[];
  icon: string;
  recommended?: boolean;
}

export const UNIVERSES: Universe[] = [
  {
    id: 'popular_etfs',
    name: 'Popular ETFs',
    description: 'Broad market, sector, and commodity ETFs - Best for beginners',
    icon: '📊',
    recommended: true,
    tickers: [
      'SPY', 'IVV', 'VOO',      // S&P 500
      'QQQ', 'QQQM',            // Nasdaq
      'VTI', 'ITOT',            // Total Market
      'IWM', 'DIA',             // Small Cap, Dow
      'XLF', 'XLK', 'XLE',      // Sector ETFs
      'GLD', 'SLV',             // Commodities
      'TLT', 'IEF',             // Bonds
    ]
  },
  {
    id: 'tech_stocks',
    name: 'Technology Stocks',
    description: 'Large-cap tech companies',
    icon: '💻',
    tickers: [
      'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
      'NVDA', 'AMD', 'INTC', 'CSCO', 'ORCL',
      'ADBE', 'CRM', 'AVGO', 'QCOM', 'TXN'
    ]
  },
  {
    id: 'banking',
    name: 'Banking & Finance',
    description: 'Major US banks and financial institutions',
    icon: '🏦',
    tickers: [
      'JPM', 'BAC', 'WFC', 'C', 'GS', 'MS',
      'BLK', 'USB', 'PNC', 'TFC', 'AXP', 'SCHW'
    ]
  },
  {
    id: 'energy',
    name: 'Energy Sector',
    description: 'Oil, gas, and energy companies',
    icon: '⚡',
    tickers: [
      'XOM', 'CVX', 'COP', 'SLB', 'EOG', 'MPC',
      'PSX', 'VLO', 'OXY', 'HAL', 'XLE'
    ]
  },
  {
    id: 'consumer',
    name: 'Consumer Goods',
    description: 'Retail, food, and consumer products',
    icon: '🛒',
    tickers: [
      'WMT', 'COST', 'TGT', 'HD', 'LOW', 'MCD',
      'SBUX', 'NKE', 'PG', 'KO', 'PEP', 'CL'
    ]
  },
  {
    id: 'healthcare',
    name: 'Healthcare',
    description: 'Pharmaceutical and healthcare companies',
    icon: '🏥',
    tickers: [
      'JNJ', 'UNH', 'PFE', 'ABBV', 'TMO', 'ABT',
      'MRK', 'LLY', 'DHR', 'AMGN', 'CVS'
    ]
  }
];

// Helper function to get universe by ID
export const getUniverseById = (id: string): Universe | undefined => {
  return UNIVERSES.find(u => u.id === id);
};

// Helper function to get recommended universe
export const getRecommendedUniverse = (): Universe => {
  return UNIVERSES.find(u => u.recommended) || UNIVERSES[0];
};
