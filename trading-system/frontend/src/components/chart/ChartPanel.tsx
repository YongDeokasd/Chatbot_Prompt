import {
  CandlestickSeries,
  HistogramSeries,
  LineSeries,
  createChart,
  type IChartApi,
  type ISeriesApi,
  type SeriesType,
} from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { Candle, IndicatorRead, TradeRecord } from "../../types";

function toSec(iso: string): number {
  return Math.floor(new Date(iso).getTime() / 1000);
}

const LINE_COLORS = ["#2196f3", "#ff9800", "#9c27b0", "#00bcd4", "#8bc34a", "#f44336"];

interface Marker {
  time: number;
  position: "aboveBar" | "belowBar";
  color: string;
  shape: "arrowUp" | "arrowDown";
  text: string;
}

function tradesToMarkers(trades: TradeRecord[]): Marker[] {
  const markers: Marker[] = [];
  for (const t of trades) {
    markers.push({
      time: toSec(t.entry_time),
      position: "belowBar",
      color: "#26a69a",
      shape: "arrowUp",
      text: `BUY @ ${t.entry_price.toFixed(2)}`,
    });
    if (t.exit_time && t.exit_price != null) {
      markers.push({
        time: toSec(t.exit_time),
        position: "aboveBar",
        color: t.pnl >= 0 ? "#26a69a" : "#ef5350",
        shape: "arrowDown",
        text: `SELL @ ${t.exit_price.toFixed(2)} (${t.return_pct.toFixed(2)}%)`,
      });
    }
  }
  return markers.sort((a, b) => a.time - b.time);
}

interface Props {
  candles: Candle[];
  indicators: IndicatorRead[];
  indicatorOutputs: Record<string, Record<string, number[]>>;
  trades?: TradeRecord[];
}

export function ChartPanel({ candles, indicators, indicatorOutputs, trades = [] }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);
  const chartRef = useRef<IChartApi | null>(null);
  const candleSeriesRef = useRef<ISeriesApi<SeriesType> | null>(null);
  const indSeriesRef = useRef<ISeriesApi<SeriesType>[]>([]);

  useEffect(() => {
    if (!containerRef.current) return;
    const chart = createChart(containerRef.current, {
      autoSize: true,
      layout: { background: { color: "#0b0e11" }, textColor: "#d1d4dc" },
      grid: { vertLines: { color: "#1c2127" }, horzLines: { color: "#1c2127" } },
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
    candleSeriesRef.current = candleSeries;

    const volSeries = chart.addSeries(HistogramSeries, {
      priceFormat: { type: "volume" },
      priceScaleId: "",
    });
    volSeries.priceScale().applyOptions({ scaleMargins: { top: 0.8, bottom: 0 } });

    candleSeries.setData(
      candles.map((c) => ({
        time: toSec(c.open_time) as never,
        open: c.open, high: c.high, low: c.low, close: c.close,
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

  // Overlay indicator lines
  useEffect(() => {
    const chart = chartRef.current;
    if (!chart || candles.length === 0) return;
    for (const s of indSeriesRef.current) chart.removeSeries(s);
    indSeriesRef.current = [];

    let colorIdx = 0;
    for (const ind of indicators) {
      const outputs = indicatorOutputs[ind.id];
      if (!outputs) continue;
      for (const key of Object.keys(outputs)) {
        const color = LINE_COLORS[colorIdx++ % LINE_COLORS.length];
        const series = chart.addSeries(LineSeries, { color, lineWidth: 1 });
        const data = outputs[key]
          .map((v, i) => ({ time: toSec(candles[i]?.open_time ?? "") as never, value: v }))
          .filter((p) => isFinite(p.value) && p.time > 0);
        series.setData(data);
        indSeriesRef.current.push(series);
      }
    }
  }, [indicators, indicatorOutputs, candles]);

  // Trade markers
  useEffect(() => {
    if (!candleSeriesRef.current || trades.length === 0) return;
    // @ts-expect-error setMarkers exists on candlestick series
    candleSeriesRef.current.setMarkers(tradesToMarkers(trades));
  }, [trades]);

  return <div ref={containerRef} className="h-[520px] w-full" />;
}
