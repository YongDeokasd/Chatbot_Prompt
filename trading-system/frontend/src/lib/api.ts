import type {
  BacktestResponse,
  BenchmarkRead,
  CandlesResponse,
  IndicatorCreate,
  IndicatorRead,
  PineConvertResponse,
  StrategyRead,
  SymbolResult,
  TimeframeInfo,
} from "../types";

const TOKEN = import.meta.env.VITE_LOCAL_API_TOKEN ?? "";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(path, {
    ...init,
    headers: {
      Authorization: `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
      ...(init?.headers ?? {}),
    },
  });
  if (!res.ok) {
    const body = await res.json().catch(() => ({ detail: res.statusText }));
    const err = new Error(body.detail ?? res.statusText) as Error & { status: number; body: unknown };
    err.status = res.status;
    err.body = body;
    throw err;
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

const get = <T>(path: string) => request<T>(path);
const post = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "POST", body: JSON.stringify(body) });
const put = <T>(path: string, body: unknown) =>
  request<T>(path, { method: "PUT", body: JSON.stringify(body) });
const del = (path: string) => request<void>(path, { method: "DELETE" });

// Market
export const fetchCandles = (
  symbol: string, exchange: string, timeframe: string, from: string, to: string,
) => {
  const q = new URLSearchParams({ symbol, exchange, timeframe, from, to });
  return get<CandlesResponse>(`/api/market/candles?${q}`);
};

// Symbols
export const searchSymbols = (q: string, category?: string) => {
  const params = new URLSearchParams({ q });
  if (category) params.set("category", category);
  return get<SymbolResult[]>(`/api/symbols/search?${params}`);
};

export const getTimeframes = (symbol: string, exchange: string) =>
  get<{ symbol: string; exchange: string; timeframes: TimeframeInfo[] }>(
    `/api/symbols/${encodeURIComponent(symbol)}/timeframes?exchange=${exchange}`,
  );

// Indicators
export const listIndicators = () => get<IndicatorRead[]>("/api/indicators");
export const createIndicator = (data: IndicatorCreate) => post<IndicatorRead>("/api/indicators", data);
export const updateIndicator = (id: string, data: Partial<IndicatorCreate>) =>
  put<IndicatorRead>(`/api/indicators/${id}`, data);
export const deleteIndicator = (id: string) => del(`/api/indicators/${id}`);
export const computeIndicator = (
  id: string,
  symbol: string, exchange: string, timeframe: string,
  from: string, to: string, params: Record<string, unknown>,
) =>
  post<Record<string, number[]>>(`/api/indicators/${id}/compute`, {
    symbol, exchange, timeframe, from, to, params,
  });

// AI
export const convertPine = (pine_code: string) =>
  post<PineConvertResponse>("/api/ai/convert-pine", { pine_code });

// Strategies
export const listStrategies = () => get<StrategyRead[]>("/api/strategies");
export const createStrategy = (data: Omit<StrategyRead, "id" | "user_id" | "created_at">) =>
  post<StrategyRead>("/api/strategies", data);
export const updateStrategy = (id: string, data: Partial<StrategyRead>) =>
  put<StrategyRead>(`/api/strategies/${id}`, data);
export const deleteStrategy = (id: string) => del(`/api/strategies/${id}`);

// Backtests
export const runBacktest = (strategy_id: string, from: string, to: string) =>
  post<BacktestResponse>("/api/backtests/run", { strategy_id, from, to });
export const listBacktests = () => get<BacktestResponse[]>("/api/backtests");
export const getBacktest = (id: string) => get<BacktestResponse>(`/api/backtests/${id}`);

// Benchmarks
export const listBenchmarks = () => get<BenchmarkRead[]>("/api/benchmarks");
export const addBenchmark = (symbol: string, exchange: string) =>
  post<BenchmarkRead>("/api/benchmarks", { symbol, exchange });
export const deleteBenchmark = (id: string) => del(`/api/benchmarks/${id}`);
