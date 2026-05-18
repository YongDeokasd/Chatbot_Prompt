import { AreaSeries, createChart } from "lightweight-charts";
import { useEffect, useRef } from "react";
import type { EquityPoint } from "../../types";

export function EquityCurve({ data }: { data: EquityPoint[] }) {
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (!ref.current || data.length === 0) return;
    const chart = createChart(ref.current, {
      autoSize: true,
      layout: { background: { color: "#0b0e11" }, textColor: "#d1d4dc" },
      grid: { vertLines: { color: "#1c2127" }, horzLines: { color: "#1c2127" } },
      rightPriceScale: { scaleMargins: { top: 0.1, bottom: 0.1 } },
      timeScale: { timeVisible: true },
    });
    const series = chart.addSeries(AreaSeries, {
      topColor: "#26a69a55",
      bottomColor: "#26a69a00",
      lineColor: "#26a69a",
      lineWidth: 2,
    });
    series.setData(
      data.map((p) => ({
        time: Math.floor(new Date(p.time).getTime() / 1000) as never,
        value: p.value,
      })),
    );
    chart.timeScale().fitContent();
    return () => chart.remove();
  }, [data]);

  return <div ref={ref} className="h-48 w-full" />;
}
