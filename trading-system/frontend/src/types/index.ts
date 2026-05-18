export interface Candle {
  open_time: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number;
}

export interface CandlesResponse {
  symbol: string;
  exchange: string;
  timeframe: string;
  candles: Candle[];
}

export interface TimeframeInfo {
  timeframe: string;
  available: boolean;
  max_days: number | null;
}

export interface SymbolResult {
  symbol: string;
  exchange: string;
  name?: string;
}

export interface ParamSchema {
  name: string;
  type: "int" | "float" | "bool";
  default: number | boolean;
  min?: number;
  max?: number;
}

export interface OutputSchema {
  outputs: string[];
}

export interface IndicatorRead {
  id: string;
  user_id: string;
  name: string;
  code: string;
  language: string;
  params_schema: ParamSchema[];
  output_schema: OutputSchema;
  is_builtin: boolean;
  created_at: string;
}

export interface IndicatorCreate {
  name: string;
  code: string;
  language?: string;
  params_schema: ParamSchema[];
  output_schema: OutputSchema;
}

export type PriceSource = "open" | "high" | "low" | "close" | "volume";
export type Operator = ">" | "<" | ">=" | "<=" | "==" | "cross_above" | "cross_below";

export type Expression =
  | { type: "indicator"; indicator_id: string; output_key: string; shift?: number }
  | { type: "constant"; value: number }
  | { type: "price"; source: PriceSource; shift?: number };

export interface Condition {
  left: Expression;
  operator: Operator;
  right: Expression;
}

export interface StrategyConfig {
  entry_conditions: Condition[];
  entry_logic: "AND" | "OR";
  exit_conditions: Condition[];
  exit_logic: "AND" | "OR";
}

export interface StrategyRead {
  id: string;
  user_id: string;
  name: string;
  symbol: string;
  exchange: string;
  timeframe: string;
  position_type: string;
  fees_bps: number;
  slippage_bps: number;
  initial_cash: number;
  config: StrategyConfig;
  created_at: string;
}

export interface TradeRecord {
  entry_time: string;
  entry_price: number;
  exit_time?: string;
  exit_price?: number;
  size: number;
  pnl: number;
  return_pct: number;
  reason: string;
}

export interface EquityPoint {
  time: string;
  value: number;
}

export interface BacktestStats {
  total_return: number;
  cagr: number;
  sharpe: number;
  sortino: number;
  calmar: number;
  max_drawdown: number;
  win_rate: number;
  profit_factor: number;
  trade_count: number;
}

export interface BacktestResponse {
  id: string;
  duration_ms: number;
  stats: BacktestStats;
  trades: TradeRecord[];
  equity_curve: EquityPoint[];
}

export interface BenchmarkRead {
  id: string;
  symbol: string;
  exchange: string;
  active: boolean;
  created_at: string;
}

export interface PineConvertResponse {
  python_code: string;
  params_schema: ParamSchema[];
  output_schema: OutputSchema;
  explanation: string;
  warnings: string[];
}
