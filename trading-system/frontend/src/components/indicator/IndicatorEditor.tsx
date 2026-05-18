import { lazy, Suspense, useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createIndicator, updateIndicator, deleteIndicator } from "../../lib/api";
import type { IndicatorRead } from "../../types";

const MonacoEditor = lazy(() =>
  import("@monaco-editor/react").then((m) => ({ default: m.default })),
);

const DEFAULT_CODE = `def compute(candles, params):
    import pandas_ta as ta
    length = int(params.get('length', 20))
    return {'value': ta.sma(candles['close'], length=length)}
`;

interface Props {
  indicator?: IndicatorRead;
  onClose: () => void;
}

export function IndicatorEditor({ indicator, onClose }: Props) {
  const qc = useQueryClient();
  const [name, setName] = useState(indicator?.name ?? "");
  const [code, setCode] = useState(indicator?.code ?? DEFAULT_CODE);
  const [error, setError] = useState<string | null>(null);

  const save = useMutation({
    mutationFn: async () => {
      const payload = {
        name,
        code,
        language: "python",
        params_schema: indicator?.params_schema ?? [],
        output_schema: indicator?.output_schema ?? { outputs: ["value"] },
      };
      return indicator
        ? updateIndicator(indicator.id, payload)
        : createIndicator(payload);
    },
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["indicators"] }); onClose(); },
    onError: (e) => setError(String(e)),
  });

  const remove = useMutation({
    mutationFn: () => deleteIndicator(indicator!.id),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["indicators"] }); onClose(); },
  });

  return (
    <div className="flex flex-col gap-3">
      <div className="flex items-center gap-3">
        <input
          className="flex-1 rounded border border-gray-600 bg-gray-800 px-3 py-1.5 text-sm text-gray-100 focus:outline-none"
          placeholder="Indicator name"
          value={name}
          onChange={(e) => setName(e.target.value)}
        />
        <button
          onClick={onClose}
          className="text-xs text-gray-500 hover:text-gray-300"
        >
          ✕ cancel
        </button>
      </div>

      <Suspense fallback={<div className="h-48 animate-pulse rounded bg-gray-800" />}>
        <MonacoEditor
          height="280px"
          language="python"
          theme="vs-dark"
          value={code}
          onChange={(v) => setCode(v ?? "")}
          options={{ minimap: { enabled: false }, fontSize: 13 }}
        />
      </Suspense>

      {error && <p className="text-xs text-red-400">{error}</p>}

      <div className="flex gap-2">
        <button
          disabled={!name || save.isPending}
          onClick={() => save.mutate()}
          className="rounded bg-blue-600 px-4 py-1.5 text-sm font-medium hover:bg-blue-500 disabled:opacity-50"
        >
          {save.isPending ? "Saving…" : "Save"}
        </button>
        {indicator && !indicator.is_builtin && (
          <button
            onClick={() => remove.mutate()}
            className="rounded bg-red-800 px-3 py-1.5 text-sm hover:bg-red-700"
          >
            Delete
          </button>
        )}
      </div>
    </div>
  );
}
