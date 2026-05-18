import type { CandlesResponse } from "../types";

const TOKEN = import.meta.env.VITE_LOCAL_API_TOKEN ?? "";

async function get<T>(path: string): Promise<T> {
  const res = await fetch(path, {
    headers: { Authorization: `Bearer ${TOKEN}` },
  });
  if (!res.ok) throw new Error(`API ${res.status}: ${await res.text()}`);
  return res.json() as Promise<T>;
}

export function fetchCandles(
  symbol: string,
  exchange: string,
  timeframe: string,
  from: string,
  to: string,
): Promise<CandlesResponse> {
  const q = new URLSearchParams({ symbol, exchange, timeframe, from, to });
  return get<CandlesResponse>(`/api/market/candles?${q}`);
}
