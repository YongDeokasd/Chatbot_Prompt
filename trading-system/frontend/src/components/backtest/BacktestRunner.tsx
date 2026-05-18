import { useState } from "react";
import { useMutation } from "@tanstack/react-query";
import { runBacktest } from "../../lib/api";
import { useChartStore, useStrategyStore } from "../../stores";

export function BacktestRunner() {
  const { activeStrategy } = useStrategyStore();
  const { setBacktestResult } = useChartStore();

  const today = new Date().toISOString().slice(0, 10);
  const yearAgo = new Date(Date.now() - 365 * 86400_000).toISOString().slice(0, 10);
  const [from, setFrom] = useState(yearAgo);
  const [to, setTo] = useState(today);
  const [error, setError] = useState<string | null>(null);

  const run = useMutation({
    mutationFn: () =>
      runBacktest(
        activeStrategy!.id,
        from + "T00:00:00Z",
        to + "T00:00:00Z",
      ),
    onSuccess: (r) => { setBacktestResult(r); setError(null); },
    onError: (e: Error & { body?: { detail?: string } }) => {
      setError(e.body?.detail ?? String(e));
    },
  });

  if (!activeStrategy) return (
    <p className="text-xs text-gray-500">Select a strategy to run backtest.</p>
  );

  return (
    <div className="flex flex-col gap-3 text-sm">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500">Backtest</h3>
      <p className="text-xs text-gray-400">Strategy: <span className="text-gray-200">{activeStrategy.name}</span></p>
      <div className="flex gap-2">
        <label className="flex flex-col gap-1 text-xs text-gray-400">
          From <input type="date" value={from} onChange={(e) => setFrom(e.target.value)}
            className="rounded border border-gray-600 bg-gray-800 px-2 py-1 text-gray-100" />
        </label>
        <label className="flex flex-col gap-1 text-xs text-gray-400">
          To <input type="date" value={to} onChange={(e) => setTo(e.target.value)}
            className="rounded border border-gray-600 bg-gray-800 px-2 py-1 text-gray-100" />
        </label>
      </div>
      {error && <p className="text-xs text-red-400">{error}</p>}
      <button
        disabled={run.isPending}
        onClick={() => run.mutate()}
        className="rounded bg-green-700 py-1.5 text-sm font-medium hover:bg-green-600 disabled:opacity-50"
      >
        {run.isPending ? "Running…" : "▶ Run Backtest"}
      </button>
    </div>
  );
}
