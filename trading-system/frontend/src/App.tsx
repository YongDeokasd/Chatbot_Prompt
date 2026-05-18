import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";
import { computeIndicator, fetchCandles } from "./lib/api";
import { useChartStore } from "./stores";
import type { IndicatorRead } from "./types";

import { ChartPanel } from "./components/chart/ChartPanel";
import { SymbolSearch } from "./components/chart/SymbolSearch";
import { TimeframeSelector } from "./components/chart/TimeframeSelector";
import { IndicatorList } from "./components/indicator/IndicatorList";
import { IndicatorEditor } from "./components/indicator/IndicatorEditor";
import { PineImporter } from "./components/indicator/PineImporter";
import { StrategyBuilder } from "./components/strategy/StrategyBuilder";
import { BacktestRunner } from "./components/backtest/BacktestRunner";
import { ResultStats } from "./components/backtest/ResultStats";
import { EquityCurve } from "./components/backtest/EquityCurve";
import { TradeList } from "./components/backtest/TradeList";
import { BenchmarkPanel } from "./components/benchmark/BenchmarkPanel";

type Panel = "indicators" | "strategy" | "backtest" | "benchmarks";

const TO = new Date().toISOString().replace(/\.\d+Z$/, "Z");
const FROM = new Date(Date.now() - 365 * 86400_000).toISOString().replace(/\.\d+Z$/, "Z");

export default function App() {
  const { symbol, exchange, timeframe, setSymbol, setTimeframe,
    activeIndicators, setIndicatorOutput, indicatorOutputs, backtestResult } = useChartStore();

  const [panel, setPanel] = useState<Panel>("indicators");
  const [editingInd, setEditingInd] = useState<IndicatorRead | "new" | null>(null);

  const { data: candleData, isLoading, error } = useQuery({
    queryKey: ["candles", symbol, exchange, timeframe, FROM, TO],
    queryFn: () => fetchCandles(symbol, exchange, timeframe, FROM, TO),
    staleTime: 60_000,
  });

  // Compute active indicators whenever candles or active set changes
  useEffect(() => {
    if (!candleData) return;
    for (const ind of activeIndicators) {
      computeIndicator(ind.id, symbol, exchange, timeframe, FROM, TO, {})
        .then((outputs) => setIndicatorOutput(ind.id, outputs))
        .catch(console.error);
    }
  }, [activeIndicators, candleData, symbol, exchange, timeframe]);

  return (
    <div className="flex h-screen bg-[#0b0e11] text-gray-200">
      {/* Sidebar */}
      <aside className="flex w-72 flex-col gap-4 overflow-y-auto border-r border-gray-800 p-4">
        {/* Symbol + TF */}
        <div className="flex flex-col gap-2">
          <SymbolSearch value={symbol} exchange={exchange} onChange={setSymbol} />
          <TimeframeSelector symbol={symbol} exchange={exchange} value={timeframe} onChange={setTimeframe} />
        </div>

        {/* Panel tabs */}
        <div className="flex flex-wrap gap-1 text-xs">
          {(["indicators", "strategy", "backtest", "benchmarks"] as Panel[]).map((p) => (
            <button
              key={p}
              onClick={() => setPanel(p)}
              className={`rounded px-2 py-1 capitalize ${panel === p ? "bg-blue-700 text-white" : "text-gray-400 hover:bg-gray-800"}`}
            >
              {p}
            </button>
          ))}
        </div>

        {/* Panel content */}
        {panel === "indicators" && (
          <div className="flex flex-col gap-4">
            {editingInd === null && (
              <>
                <IndicatorList onEdit={(ind) => setEditingInd(ind)} />
                <button
                  onClick={() => setEditingInd("new")}
                  className="rounded border border-dashed border-gray-600 py-1.5 text-xs text-gray-500 hover:border-blue-500 hover:text-blue-400"
                >
                  + New indicator
                </button>
                <PineImporter />
              </>
            )}
            {editingInd !== null && (
              <IndicatorEditor
                indicator={editingInd === "new" ? undefined : editingInd}
                onClose={() => setEditingInd(null)}
              />
            )}
          </div>
        )}

        {panel === "strategy" && <StrategyBuilder />}

        {panel === "backtest" && (
          <div className="flex flex-col gap-4">
            <BacktestRunner />
            {backtestResult && (
              <>
                <p className="text-xs text-gray-500">
                  Completed in {backtestResult.duration_ms}ms · {backtestResult.trades.length} trades
                </p>
                <ResultStats stats={backtestResult.stats} />
              </>
            )}
          </div>
        )}

        {panel === "benchmarks" && <BenchmarkPanel />}
      </aside>

      {/* Main chart area */}
      <main className="flex flex-1 flex-col gap-2 overflow-auto p-4">
        <h1 className="text-sm font-semibold text-gray-300">
          {symbol} · {timeframe}
        </h1>

        {isLoading && <p className="text-xs text-gray-500">Loading candles…</p>}
        {error && <p className="text-xs text-red-400">{String(error)}</p>}

        {candleData && (
          <ChartPanel
            candles={candleData.candles}
            indicators={activeIndicators}
            indicatorOutputs={indicatorOutputs}
            trades={backtestResult?.trades ?? []}
          />
        )}

        {/* Backtest result bottom panels */}
        {backtestResult && (
          <div className="flex flex-col gap-3 mt-2">
            <EquityCurve data={backtestResult.equity_curve} />
            <TradeList trades={backtestResult.trades} />
          </div>
        )}
      </main>
    </div>
  );
}
