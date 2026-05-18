import type { TradeRecord } from "../../types";

function fmt(iso: string) {
  return new Date(iso).toLocaleString();
}

export function TradeList({ trades }: { trades: TradeRecord[] }) {
  return (
    <div className="overflow-auto rounded border border-gray-700">
      <table className="w-full text-xs">
        <thead>
          <tr className="border-b border-gray-700 bg-gray-800 text-gray-400">
            <th className="px-3 py-2 text-left">Entry</th>
            <th className="px-3 py-2 text-right">Entry $</th>
            <th className="px-3 py-2 text-left">Exit</th>
            <th className="px-3 py-2 text-right">Exit $</th>
            <th className="px-3 py-2 text-right">PnL</th>
            <th className="px-3 py-2 text-right">Return</th>
          </tr>
        </thead>
        <tbody>
          {trades.map((t, i) => (
            <tr
              key={i}
              className={`border-b border-gray-800 ${t.pnl >= 0 ? "text-green-300" : "text-red-300"}`}
            >
              <td className="px-3 py-1.5 text-gray-400">{fmt(t.entry_time)}</td>
              <td className="px-3 py-1.5 text-right">{t.entry_price.toFixed(2)}</td>
              <td className="px-3 py-1.5 text-gray-400">{t.exit_time ? fmt(t.exit_time) : "—"}</td>
              <td className="px-3 py-1.5 text-right">{t.exit_price?.toFixed(2) ?? "—"}</td>
              <td className="px-3 py-1.5 text-right font-medium">{t.pnl.toFixed(2)}</td>
              <td className="px-3 py-1.5 text-right">{t.return_pct.toFixed(2)}%</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
