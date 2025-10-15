// Type definitions for Implied Volatility Surface

export interface OptionContractIV {
  strike: number;
  moneyness: number;
  time_to_expiry: number;
  bid: number;
  ask: number;
  mid_price: number;
  volume: number;
  open_interest: number;
  implied_volatility: number | null;
  expiration: string;
}

export interface IVRangeStats {
  min: number | null;
  max: number | null;
  mean: number | null;
  std: number | null;
}

export interface IVSurfaceMetrics {
  atm_call_iv: number | null;
  atm_put_iv: number | null;
  atm_iv_avg: number | null;
  put_call_skew: number | null;
  iv_range_calls: IVRangeStats;
  iv_range_puts: IVRangeStats;
  total_call_contracts: number;
  total_put_contracts: number;
  successful_call_ivs: number;
  successful_put_ivs: number;
  expiration_dates: string[];
}

export interface IVSurfaceResponse {
  ticker: string;
  spot_price: number;
  risk_free_rate: number;
  calls: OptionContractIV[];
  puts: OptionContractIV[];
  metrics: IVSurfaceMetrics;
}

export interface IVSurfaceError {
  error: string;
  message: string;
  ticker?: string;
}

export type ExpirationFilter = 'first' | 'near_term' | 'all';

export interface IVSurfaceRequest {
  ticker: string;
  expiration_filter?: ExpirationFilter;
  min_volume?: number;
}
