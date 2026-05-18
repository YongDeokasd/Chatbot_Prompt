import {
  CandlestickSeries,
  HistogramSeries,
  createChart,
  type IChartApi,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { Candle } from "../../types";

function toSec(iso: string): number {
  return Math.floor(new Date(iso).getTime() / 1000);
}

export function ChartPanel({ candles }: { candles: Candle[] }) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: { background: { color: "#0b0e11" }, textColor: "#d1d4dc" },
      grid: {
        vertLines: { color: "#1c2127" },
        horzLines: { color: "#1c2127" },
      },
      timeScale: { timeVisible: true },
    });
    chartRef.current = chart;

    const candleSeries = chart.addSeries(CandlestickSeries, {
      upColor: "#26a69a",
      downColor: "#ef5350",
      wickUpColor: "#26a69a",
      wickDownColor: "#ef5350",
      borderVisible: false,
    });
    const volSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "",
    });
    volSeries.priceScale().applyOptions({
      scaleMargins: { top: 0.8, bottom: 0 },
    });

    candleSeries.setData(
      candles.map((c) => ({
        time: toSec(c.open_time) as never,
        open: c.open,
        high: c.high,
        low: c.low,
        close: c.close,
      })),
    );
    volSeries.setData(
      candles.map((c) => ({
        time: toSec(c.open_time) as never,
        value: c.volume,
        color: c.close >= c.open ? "#26a69a55" : "#ef535055",
      })),
    );
    chart.timeScale().fitContent();

    return () => chart.remove();
  }, [candles]);

  return <div ref={containerRef} className="h-[600px] w-full" />;
}
