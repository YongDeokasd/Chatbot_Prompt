import { useQuery } from "@tanstack/react-query";
import { ChartPanel } from "./components/chart/ChartPanel";
import { fetchCandles } from "./lib/api";

const NOW = new Date();
const YEAR_AGO = new Date(NOW.getTime() - 365 * 24 * 3600 * 1000);

export default function App() {
  const { data, isLoading, error } = useQuery({
    queryKey: ["candles", "BTCUSDT", "1h"],
    queryFn: () =>
      fetchCandles(
        "BTCUSDT",
        "binance",
        "1h",
        YEAR_AGO.toISOString().replace(/\.\d+Z$/, "Z"),
        NOW.toISOString().replace(/\.\d+Z$/, "Z"),
      ),
  });

  return (
    <div className="min-h-screen bg-[#0b0e11] p-4 text-gray-200">
      <h1 className="mb-4 text-xl font-semibold">
        Trading System — BTCUSDT 1h
      </h1>
      {isLoading && <p>Loading candles…</p>}
      {error && <p className="text-red-400">{String(error)}</p>}
      {data && <ChartPanel candles={data.candles} />}
    </div>
  );
}
