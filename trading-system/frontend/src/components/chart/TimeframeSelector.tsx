import { useEffect, useState } from "react";
import { getTimeframes } from "../../lib/api";
import type { TimeframeInfo } from "../../types";

const ALL_TFS = ["1m", "5m", "15m", "1h", "4h", "1d", "1w"];

interface Props {
  symbol: string;
  exchange: string;
  value: string;
  onChange: (tf: string) => void;
}

export function TimeframeSelector({ symbol, exchange, value, onChange }: Props) {
  const [infos, setInfos] = useState<TimeframeInfo[]>(
    ALL_TFS.map((tf) => ({ timeframe: tf, available: true, max_days: null })),
  );

  useEffect(() => {
    getTimeframes(symbol, exchange)
      .then((r) => setInfos(r.timeframes))
      .catch(() => {});
  }, [symbol, exchange]);

  return (
    <div className="flex gap-1">
      {infos.map((info) => (
        <button
          key={info.timeframe}
          disabled={!info.available}
          title={!info.available ? `Max ${info.max_days}d` : undefined}
          onClick={() => info.available && onChange(info.timeframe)}
          className={`rounded px-2.5 py-1 text-xs font-medium transition-colors
            ${!info.available ? "cursor-not-allowed text-gray-600" : ""}
            ${info.available && value === info.timeframe
              ? "bg-blue-600 text-white"
              : info.available
              ? "text-gray-400 hover:bg-gray-700 hover:text-gray-100"
              : ""
            }`}
        >
          {info.timeframe}
        </button>
      ))}
    </div>
  );
}
