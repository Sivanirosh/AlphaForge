export interface Price {
  ticker: string;
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface Metric {
  ticker: string;
  date: string;
  log_return: number | null;
  rolling_vol: number | null;
  sharpe_ratio: number | null;
}

export interface BetaDecomposition {
  ticker: string;
  computed_at: string;
  window: number;
  market_beta: number;
  smb_beta: number | null;
  hml_beta: number | null;
  r_squared: number;
}

export interface VolatilityPoint {
  date: string;
  rolling_vol: number | null;
}

export interface VolatilityResponse {
  ticker: string;
  window: number;
  series: VolatilityPoint[];
}

export interface TickerListResponse {
  tickers: string[];
}
