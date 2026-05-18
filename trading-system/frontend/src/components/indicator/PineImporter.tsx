import { useState } from "react";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { convertPine, createIndicator } from "../../lib/api";

export function PineImporter() {
  const qc = useQueryClient();
  const [pine, setPine] = useState("");
  const [name, setName] = useState("");
  const [result, setResult] = useState<{ python_code: string; explanation: string; warnings: string[] } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const convert = useMutation({
    mutationFn: () => convertPine(pine),
    onSuccess: (r) => { setResult(r); setError(null); },
    onError: (e: Error & { body?: { unsupported_tokens?: string[] } }) => {
      const tokens = e.body?.unsupported_tokens;
      setError(tokens ? `Unsupported: ${tokens.join(", ")}` : String(e));
      setResult(null);
    },
  });

  const save = useMutation({
    mutationFn: () =>
      createIndicator({
        name,
        code: result!.python_code,
        language: "python",
        params_schema: [],
        output_schema: { outputs: ["value"] },
      }),
    onSuccess: () => { qc.invalidateQueries({ queryKey: ["indicators"] }); setResult(null); setPine(""); setName(""); },
  });

  return (
    <div className="flex flex-col gap-3">
      <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500">
        Pine Script → Python
      </h3>
      <textarea
        className="h-36 rounded border border-gray-600 bg-gray-800 p-2 font-mono text-xs text-gray-200 focus:outline-none"
        placeholder={`//@version=5\nindicator("RSI")\nplot(ta.rsi(close, 14))`}
        value={pine}
        onChange={(e) => setPine(e.target.value)}
      />
      <button
        disabled={!pine || convert.isPending}
        onClick={() => convert.mutate()}
        className="rounded bg-purple-700 px-4 py-1.5 text-sm hover:bg-purple-600 disabled:opacity-50"
      >
        {convert.isPending ? "Converting…" : "Convert"}
      </button>

      {error && <p className="text-xs text-red-400">{error}</p>}

      {result && (
        <div className="flex flex-col gap-2 rounded border border-gray-700 bg-gray-800 p-3">
          <p className="text-xs text-gray-400">{result.explanation}</p>
          {result.warnings.map((w, i) => (
            <p key={i} className="text-xs text-yellow-400">⚠ {w}</p>
          ))}
          <pre className="max-h-32 overflow-auto rounded bg-gray-900 p-2 text-xs text-green-300">
            {result.python_code}
          </pre>
          <div className="flex gap-2">
            <input
              className="flex-1 rounded border border-gray-600 bg-gray-700 px-2 py-1 text-sm text-gray-100 focus:outline-none"
              placeholder="Name this indicator"
              value={name}
              onChange={(e) => setName(e.target.value)}
            />
            <button
              disabled={!name || save.isPending}
              onClick={() => save.mutate()}
              className="rounded bg-blue-600 px-3 py-1 text-sm hover:bg-blue-500 disabled:opacity-50"
            >
              {save.isPending ? "Saving…" : "Save"}
            </button>
          </div>
        </div>
      )}
    </div>
  );
}
