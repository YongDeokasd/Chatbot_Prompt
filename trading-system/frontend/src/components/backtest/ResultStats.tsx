import type { BacktestStats } from "../../types";

const pct = (v: number) => `${(v * 100).toFixed(2)}%`;
const fmt = (v: number) => v.toFixed(3);

const METRICS: { key: keyof BacktestStats; label: string; fmt: (v: number) => string }[] = [
  { key: "total_return", label: "Total Return", fmt: pct },
  { key: "cagr", label: "CAGR", fmt: pct },
  { key: "sharpe", label: "Sharpe", fmt: fmt },
  { key: "sortino", label: "Sortino", fmt: fmt },
  { key: "calmar", label: "Calmar", fmt: fmt },
  { key: "max_drawdown", label: "Max Drawdown", fmt: pct },
  { key: "win_rate", label: "Win Rate", fmt: pct },
  { key: "profit_factor", label: "Profit Factor", fmt: fmt },
  { key: "trade_count", label: "Trades", fmt: (v) => String(v) },
];

export function ResultStats({ stats }: { stats: BacktestStats }) {
  return (
    <div className="grid grid-cols-3 gap-2">
      {METRICS.map(({ key, label, fmt: f }) => {
        const v = stats[key] as number;
        const isNeg = typeof v === "number" && v < 0;
        return (
          <div key={key} className="rounded bg-gray-800 p-2 text-center">
            <p className="text-xs text-gray-500">{label}</p>
            <p className={`text-sm font-semibold ${isNeg ? "text-red-400" : "text-green-400"}`}>
              {f(v)}
            </p>
          </div>
        );
      })}
    </div>
  );
}
