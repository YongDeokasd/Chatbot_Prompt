import { useQuery } from "@tanstack/react-query";
import { listIndicators } from "../../lib/api";
import { useChartStore } from "../../stores";
import type { IndicatorRead } from "../../types";

interface Props {
  onEdit: (ind: IndicatorRead) => void;
}

export function IndicatorList({ onEdit }: Props) {
  const { data: indicators = [] } = useQuery({
    queryKey: ["indicators"],
    queryFn: listIndicators,
  });

  const { activeIndicators, toggleIndicator } = useChartStore();
  const activeIds = new Set(activeIndicators.map((i) => i.id));

  return (
    <div className="flex flex-col gap-1">
      <h3 className="mb-1 text-xs font-semibold uppercase tracking-wider text-gray-500">
        Indicators
      </h3>
      {indicators.map((ind) => (
        <div
          key={ind.id}
          className="flex items-center justify-between rounded px-2 py-1.5 text-sm hover:bg-gray-800"
        >
          <label className="flex cursor-pointer items-center gap-2">
            <input
              type="checkbox"
              checked={activeIds.has(ind.id)}
              onChange={() => toggleIndicator(ind)}
              className="accent-blue-500"
            />
            <span className="text-gray-200">{ind.name}</span>
            {ind.is_builtin && (
              <span className="rounded bg-gray-700 px-1 py-0.5 text-xs text-gray-400">built-in</span>
            )}
          </label>
          {!ind.is_builtin && (
            <button
              onClick={() => onEdit(ind)}
              className="text-xs text-gray-500 hover:text-blue-400"
            >
              edit
            </button>
          )}
        </div>
      ))}
    </div>
  );
}
