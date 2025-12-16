// API Types for HRP Analysis

export interface HRPRequest {
  tickers: string[];
  start_date: string;
  end_date: string;
  linkage_method?: 'single' | 'complete' | 'average' | 'ward';
}

export interface DendrogramNode {
  name: string;
  height: number;
  distance?: number; // For backward compatibility (alias for height)
  children?: DendrogramNode[] | null;
}

export interface HeatmapCell {
  x: string;
  y: string;
  value: number;
}

export interface HRPResponse {
  ordered_tickers: string[];
  dendrogram_data: DendrogramNode;
  heatmap_data: HeatmapCell[];
  cluster_leaf_map: Record<string, string[]>;
  linkage_method: string;
  data_points: number;
}

export interface CorrelationRequest {
  tickers: string[];
  start_date: string;
  end_date: string;
}

export interface CorrelationResponse {
  tickers: string[];
  correlation_matrix: number[][];
  start_date: string;
  end_date: string;
  data_points: number;
}

// Statistical Arbitrage Types

// Pair Testing
export interface PairTestRequest {
  ticker_a: string;
  ticker_b: string;
  start_date: string;
  end_date: string;
}

export interface CointResult {
  p_value: number;
  test_statistic: number;
  is_cointegrated: boolean;
  hedge_ratio: number;
  half_life: number;
  spread_mean: number;
  spread_std: number;
  correlation: number;
}

// Find Pairs
export interface FindPairsRequest {
  tickers: string[];
  start_date: string;
  end_date: string;
  p_value_threshold?: number;
}

export interface CointegratedPair {
  asset_1: string;
  asset_2: string;
  p_value: number;
  test_statistic: number;
  hedge_ratio: number;
  half_life: number;
  correlation: number;
}

export interface FindPairsResponse {
  pairs: CointegratedPair[];
  total_combinations_tested: number;
  cointegrated_count: number;
}

// Spread Analysis
export interface SpreadAnalysisRequest {
  ticker_a: string;
  ticker_b: string;
  start_date: string;
  end_date: string;
  window?: number;
  entry_threshold?: number;
  exit_threshold?: number;
}

export interface SpreadPoint {
  date: string;
  spread: number;
  zscore: number;
  signal: 'long' | 'short' | 'exit' | null;
}

export interface SpreadStatistics {
  mean: number;
  std: number;
  min: number;
  max: number;
}

export interface SpreadAnalysisResponse {
  ticker_a: string;
  ticker_b: string;
  hedge_ratio: number;
  half_life: number;
  spread_data: SpreadPoint[];
  statistics: SpreadStatistics;
}

// UI State Types
export interface AnalysisState {
  loading: boolean;
  error: string | null;
  data: HRPResponse | null;
}

// Monte Carlo Simulation Types
export interface MonteCarloRequest {
  tickers: string[];
  start_date: string;
  end_date: string;
  num_simulations: number;
  num_days: number;
  weighting?: 'equal' | 'min_var';
}

export interface AssetStatistics {
  mean: number;
  std: number;
  percentile_5: number;
  percentile_50: number;
  percentile_95: number;
}

export interface PortfolioStatistics {
  mean: number;
  std: number;
  percentile_5: number;
  percentile_25: number;
  percentile_50: number;
  percentile_75: number;
  percentile_95: number;
  min: number;
  max: number;
}

export interface MonteCarloResponse {
  tickers: string[];
  num_simulations: number;
  num_days: number;
  portfolio_statistics: PortfolioStatistics;
  asset_statistics: Record<string, AssetStatistics>;
  sample_paths: number[][];
  final_value_distribution: number[];
  execution_time_ms: number;
  portfolio_weights?: number[];
  debug_inputs?: {
     mean_returns: number[];
     cov_matrix: number[][];
     initial_prices: number[];
     portfolio_weights: number[];
     raw_prices?: Record<string, number[]>; // Added for debugging data pipeline
  };
}

