import { useEffect, useState } from "react";
import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { createStrategy, listIndicators, listStrategies, updateStrategy } from "../../lib/api";
import { useChartStore, useStrategyStore } from "../../stores";
import type { Condition, StrategyConfig, StrategyRead } from "../../types";
import { ConditionRow } from "./ConditionRow";

const DEFAULT_CONDITION: Condition = {
  left: { type: "price", source: "close" },
  operator: "cross_above",
  right: { type: "indicator", indicator_id: "", output_key: "value" },
};

export function StrategyBuilder() {
  const qc = useQueryClient();
  const { symbol, exchange, timeframe } = useChartStore();
  const { strategies, activeStrategy, setStrategies, setActive } = useStrategyStore();

  const { data: indicators = [] } = useQuery({ queryKey: ["indicators"], queryFn: listIndicators });
  const { data: stratList = [] } = useQuery({
    queryKey: ["strategies"],
    queryFn: listStrategies,
    onSuccess: setStrategies,
  } as Parameters<typeof useQuery>[0]);

  const [name, setName] = useState("");
  const [entryConditions, setEntry] = useState<Condition[]>([{ ...DEFAULT_CONDITION }]);
  const [entryLogic, setEntryLogic] = useState<"AND" | "OR">("AND");
  const [exitConditions, setExit] = useState<Condition[]>([{ ...DEFAULT_CONDITION }]);
  const [exitLogic, setExitLogic] = useState<"AND" | "OR">("AND");
  const [fees, setFees] = useState(10);
  const [slip, setSlip] = useState(5);
  const [cash, setCash] = useState(10000);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (activeStrategy) {
      setName(activeStrategy.name);
      setEntry(activeStrategy.config.entry_conditions);
      setEntryLogic(activeStrategy.config.entry_logic);
      setExit(activeStrategy.config.exit_conditions);
      setExitLogic(activeStrategy.config.exit_logic);
      setFees(activeStrategy.fees_bps);
      setSlip(activeStrategy.slippage_bps);
      setCash(activeStrategy.initial_cash);
    }
  }, [activeStrategy]);

  const config: StrategyConfig = {
    entry_conditions: entryConditions,
    entry_logic: entryLogic,
    exit_conditions: exitConditions,
    exit_logic: exitLogic,
  };

  const save = useMutation({
    mutationFn: () => {
      const payload = {
        name, symbol, exchange, timeframe,
        position_type: "long",
        fees_bps: fees, slippage_bps: slip, initial_cash: cash, config,
      };
      return activeStrategy
        ? updateStrategy(activeStrategy.id, payload)
        : createStrategy(payload as Omit<StrategyRead, "id" | "user_id" | "created_at">);
    },
    onSuccess: (s) => {
      qc.invalidateQueries({ queryKey: ["strategies"] });
      setActive(s);
      setError(null);
    },
    onError: (e) => setError(String(e)),
  });

  const addCondition = (side: "entry" | "exit") => {
    const cond: Condition = {
      left: { type: "price", source: "close" },
      operator: ">",
      right: { type: "constant", value: 0 },
    };
    if (side === "entry") setEntry((p) => [...p, cond]);
    else setExit((p) => [...p, cond]);
  };

  return (
    <div className="flex flex-col gap-4 text-sm">
      <div className="flex items-center justify-between">
        <h3 className="text-xs font-semibold uppercase tracking-wider text-gray-500">Strategy Builder</h3>
        <select
          className="rounded border border-gray-600 bg-gray-800 px-2 py-1 text-xs text-gray-200"
          value={activeStrategy?.id ?? ""}
          onChange={(e) => setActive(strategies.find((s) => s.id === e.target.value) ?? null)}
        >
          <option value="">New strategy</option>
          {strategies.map((s) => <option key={s.id} value={s.id}>{s.name}</option>)}
        </select>
      </div>

      <input
        className="rounded border border-gray-600 bg-gray-800 px-2 py-1.5 text-sm text-gray-100 focus:outline-none"
        placeholder="Strategy name"
        value={name}
        onChange={(e) => setName(e.target.value)}
      />

      {/* Entry */}
      <Section label="Entry">
        <LogicToggle value={entryLogic} onChange={setEntryLogic} />
        {entryConditions.map((c, i) => (
          <ConditionRow
            key={i} condition={c} indicators={indicators}
            onChange={(nc) => setEntry((p) => p.map((x, j) => j === i ? nc : x))}
            onRemove={() => setEntry((p) => p.filter((_, j) => j !== i))}
          />
        ))}
        <button onClick={() => addCondition("entry")} className="text-xs text-blue-400 hover:underline">+ add condition</button>
      </Section>

      {/* Exit */}
      <Section label="Exit">
        <LogicToggle value={exitLogic} onChange={setExitLogic} />
        {exitConditions.map((c, i) => (
          <ConditionRow
            key={i} condition={c} indicators={indicators}
            onChange={(nc) => setExit((p) => p.map((x, j) => j === i ? nc : x))}
            onRemove={() => setExit((p) => p.filter((_, j) => j !== i))}
          />
        ))}
        <button onClick={() => addCondition("exit")} className="text-xs text-blue-400 hover:underline">+ add condition</button>
      </Section>

      {/* Params */}
      <div className="grid grid-cols-3 gap-2 text-xs">
        <label className="flex flex-col gap-1 text-gray-400">
          Fees (bps) <input type="number" value={fees} onChange={(e) => setFees(+e.target.value)} className="rounded border border-gray-600 bg-gray-800 px-2 py-1 text-gray-100" />
        </label>
        <label className="flex flex-col gap-1 text-gray-400">
          Slippage (bps) <input type="number" value={slip} onChange={(e) => setSlip(+e.target.value)} className="rounded border border-gray-600 bg-gray-800 px-2 py-1 text-gray-100" />
        </label>
        <label className="flex flex-col gap-1 text-gray-400">
          Capital <input type="number" value={cash} onChange={(e) => setCash(+e.target.value)} className="rounded border border-gray-600 bg-gray-800 px-2 py-1 text-gray-100" />
        </label>
      </div>

      {error && <p className="text-xs text-red-400">{error}</p>}
      <button
        disabled={!name || save.isPending}
        onClick={() => save.mutate()}
        className="rounded bg-blue-600 py-1.5 text-sm font-medium hover:bg-blue-500 disabled:opacity-50"
      >
        {save.isPending ? "Saving…" : "Save Strategy"}
      </button>
    </div>
  );
}

function Section({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <div className="flex flex-col gap-2 rounded border border-gray-700 p-3">
      <span className="text-xs font-semibold text-gray-400">{label}</span>
      {children}
    </div>
  );
}

function LogicToggle({ value, onChange }: { value: "AND" | "OR"; onChange: (v: "AND" | "OR") => void }) {
  return (
    <div className="flex gap-1 text-xs">
      {(["AND", "OR"] as const).map((v) => (
        <button
          key={v}
          onClick={() => onChange(v)}
          className={`rounded px-2 py-0.5 ${value === v ? "bg-blue-600 text-white" : "text-gray-400 hover:bg-gray-700"}`}
        >
          {v}
        </button>
      ))}
    </div>
  );
}
