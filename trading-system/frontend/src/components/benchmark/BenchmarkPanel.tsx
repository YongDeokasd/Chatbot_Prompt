import { useEffect } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { addBenchmark, deleteBenchmark, listBenchmarks } from "../../lib/api";
import { useRealtimeStore } from "../../stores";
import { PriceStream } from "../../lib/ws";

export function BenchmarkPanel() {
  const qc = useQueryClient();
  const { prices, setPrice } = useRealtimeStore();
  const { data: benchmarks = [] } = useQuery({ queryKey: ["benchmarks"], queryFn: listBenchmarks });

  useEffect(() => {
    const stream = new PriceStream(setPrice);
    stream.start();
    return () => stream.stop();
  }, [setPrice]);

  const add = useMutation({
    mutationFn: (sym: string) => addBenchmark(sym.toUpperCase(), sym.toUpperCase().includes("USDT") ? "binance" : "yfinance"),
    onSuccess: () => qc.invalidateQueries({ queryKey: ["benchmarks"] }),
  });

  const remove = useMutation({
    mutationFn: deleteBenchmark,
    onSuccess: () => qc.invalidateQueries({ queryKey: ["benchmarks"] }),
  });

  return (
    <div className="flex flex-col gap-2">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500">Benchmarks</h3>
      {benchmarks.map((b) => (
        <div key={b.id} className="flex items-center justify-between rounded bg-gray-800 px-3 py-2">
          <span className="text-sm font-medium text-gray-100">{b.symbol}</span>
          <div className="flex items-center gap-3">
            {prices[b.symbol] != null && (
              <span className="font-mono text-sm text-green-400">
                {prices[b.symbol].toLocaleString(undefined, { minimumFractionDigits: 2 })}
              </span>
            )}
            <button
              onClick={() => remove.mutate(b.id)}
              className="text-xs text-gray-600 hover:text-red-400"
            >
              ✕
            </button>
          </div>
        </div>
      ))}
      <form
        onSubmit={(e) => {
          e.preventDefault();
          const fd = new FormData(e.currentTarget);
          const sym = String(fd.get("symbol") ?? "").trim();
          if (sym) { add.mutate(sym); (e.target as HTMLFormElement).reset(); }
        }}
        className="flex gap-2"
      >
        <input
          name="symbol"
          className="flex-1 rounded border border-gray-600 bg-gray-800 px-2 py-1 text-sm text-gray-100 focus:outline-none"
          placeholder="BTCUSDT or AAPL"
        />
        <button type="submit" className="rounded bg-gray-700 px-3 py-1 text-sm hover:bg-gray-600">
          + Add
        </button>
      </form>
    </div>
  );
}
