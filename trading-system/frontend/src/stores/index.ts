import { create } from "zustand";
import type { BacktestResponse, IndicatorRead, StrategyRead, TradeRecord } from "../types";

interface ChartState {
  symbol: string;
  exchange: string;
  timeframe: string;
  activeIndicators: IndicatorRead[];
  indicatorOutputs: Record<string, Record<string, number[]>>;
  backtestResult: BacktestResponse | null;
  setSymbol: (symbol: string, exchange: string) => void;
  setTimeframe: (tf: string) => void;
  toggleIndicator: (ind: IndicatorRead) => void;
  setIndicatorOutput: (id: string, outputs: Record<string, number[]>) => void;
  setBacktestResult: (r: BacktestResponse | null) => void;
}

export const useChartStore = create<ChartState>((set) => ({
  symbol: "BTCUSDT",
  exchange: "binance",
  timeframe: "1h",
  activeIndicators: [],
  indicatorOutputs: {},
  backtestResult: null,

  setSymbol: (symbol, exchange) => set({ symbol, exchange, activeIndicators: [], indicatorOutputs: {} }),
  setTimeframe: (timeframe) => set({ timeframe }),
  toggleIndicator: (ind) =>
    set((s) => ({
      activeIndicators: s.activeIndicators.find((i) => i.id === ind.id)
        ? s.activeIndicators.filter((i) => i.id !== ind.id)
        : [...s.activeIndicators, ind],
    })),
  setIndicatorOutput: (id, outputs) =>
    set((s) => ({ indicatorOutputs: { ...s.indicatorOutputs, [id]: outputs } })),
  setBacktestResult: (backtestResult) => set({ backtestResult }),
}));

interface StrategyState {
  strategies: StrategyRead[];
  activeStrategy: StrategyRead | null;
  setStrategies: (s: StrategyRead[]) => void;
  setActive: (s: StrategyRead | null) => void;
}

export const useStrategyStore = create<StrategyState>((set) => ({
  strategies: [],
  activeStrategy: null,
  setStrategies: (strategies) => set({ strategies }),
  setActive: (activeStrategy) => set({ activeStrategy }),
}));

interface RealtimeState {
  prices: Record<string, number>;
  setPrice: (symbol: string, price: number) => void;
}

export const useRealtimeStore = create<RealtimeState>((set) => ({
  prices: {},
  setPrice: (symbol, price) =>
    set((s) => ({ prices: { ...s.prices, [symbol]: price } })),
}));
