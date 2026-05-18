import { useEffect, useRef, useState } from "react";
import { searchSymbols } from "../../lib/api";
import type { SymbolResult } from "../../types";

interface Props {
  value: string;
  exchange: string;
  onChange: (symbol: string, exchange: string) => void;
}

export function SymbolSearch({ value, exchange, onChange }: Props) {
  const [query, setQuery] = useState(value);
  const [results, setResults] = useState<SymbolResult[]>([]);
  const [open, setOpen] = useState(false);
  const timer = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    if (!query || query.length < 1) { setResults([]); return; }
    if (timer.current) clearTimeout(timer.current);
    timer.current = setTimeout(async () => {
      try {
        const res = await searchSymbols(query.toUpperCase());
        setResults(res);
        setOpen(true);
      } catch {}
    }, 300);
  }, [query]);

  return (
    <div className="relative">
      <input
        className="w-48 rounded border border-gray-600 bg-gray-800 px-3 py-1.5 text-sm text-gray-100 focus:outline-none focus:ring-1 focus:ring-blue-500"
        value={query}
        onChange={(e) => setQuery(e.target.value)}
        onFocus={() => results.length > 0 && setOpen(true)}
        placeholder="Symbol (e.g. BTCUSDT)"
      />
      {open && results.length > 0 && (
        <ul className="absolute z-50 mt-1 max-h-56 w-64 overflow-auto rounded border border-gray-600 bg-gray-800 shadow-lg">
          {results.map((r) => (
            <li
              key={`${r.exchange}-${r.symbol}`}
              className="flex cursor-pointer items-center justify-between px-3 py-2 text-sm hover:bg-gray-700"
              onClick={() => {
                setQuery(r.symbol);
                setOpen(false);
                onChange(r.symbol, r.exchange);
              }}
            >
              <span className="font-medium text-gray-100">{r.symbol}</span>
              <span className="text-xs text-gray-400">{r.exchange}</span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}
