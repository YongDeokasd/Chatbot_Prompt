import type { Condition, Expression, IndicatorRead, Operator } from "../../types";

const OPERATORS: Operator[] = [">", "<", ">=", "<=", "==", "cross_above", "cross_below"];

interface Props {
  condition: Condition;
  indicators: IndicatorRead[];
  onChange: (c: Condition) => void;
  onRemove: () => void;
}

function ExprEditor({
  expr,
  indicators,
  onChange,
}: {
  expr: Expression;
  indicators: IndicatorRead[];
  onChange: (e: Expression) => void;
}) {
  return (
    <div className="flex items-center gap-1">
      <select
        className="rounded border border-gray-600 bg-gray-800 px-1.5 py-1 text-xs text-gray-200"
        value={expr.type}
        onChange={(e) => {
          const t = e.target.value as Expression["type"];
          if (t === "constant") onChange({ type: "constant", value: 0 });
          else if (t === "price") onChange({ type: "price", source: "close" });
          else onChange({ type: "indicator", indicator_id: indicators[0]?.id ?? "", output_key: "value" });
        }}
      >
        <option value="price">Price</option>
        <option value="constant">Constant</option>
        <option value="indicator">Indicator</option>
      </select>

      {expr.type === "price" && (
        <select
          className="rounded border border-gray-600 bg-gray-800 px-1.5 py-1 text-xs text-gray-200"
          value={expr.source}
          onChange={(e) => onChange({ ...expr, source: e.target.value as typeof expr.source })}
        >
          {["open", "high", "low", "close", "volume"].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      )}

      {expr.type === "constant" && (
        <input
          type="number"
          className="w-20 rounded border border-gray-600 bg-gray-800 px-1.5 py-1 text-xs text-gray-200"
          value={expr.value}
          onChange={(e) => onChange({ ...expr, value: parseFloat(e.target.value) || 0 })}
        />
      )}

      {expr.type === "indicator" && (
        <>
          <select
            className="rounded border border-gray-600 bg-gray-800 px-1.5 py-1 text-xs text-gray-200"
            value={expr.indicator_id}
            onChange={(e) => {
              const ind = indicators.find((i) => i.id === e.target.value);
              onChange({ ...expr, indicator_id: e.target.value, output_key: ind?.output_schema.outputs[0] ?? "value" });
            }}
          >
            {indicators.map((i) => (
              <option key={i.id} value={i.id}>{i.name}</option>
            ))}
          </select>
          <select
            className="rounded border border-gray-600 bg-gray-800 px-1.5 py-1 text-xs text-gray-200"
            value={expr.output_key}
            onChange={(e) => onChange({ ...expr, output_key: e.target.value })}
          >
            {(indicators.find((i) => i.id === expr.indicator_id)?.output_schema.outputs ?? ["value"]).map(
              (k) => <option key={k} value={k}>{k}</option>,
            )}
          </select>
        </>
      )}

      <input
        type="number"
        title="Shift (bars back)"
        className="w-12 rounded border border-gray-600 bg-gray-800 px-1 py-1 text-xs text-gray-400"
        value={"shift" in expr ? (expr.shift ?? 0) : 0}
        onChange={(e) => onChange({ ...expr, shift: parseInt(e.target.value) || 0 } as Expression)}
        placeholder="shift"
      />
    </div>
  );
}

export function ConditionRow({ condition, indicators, onChange, onRemove }: Props) {
  return (
    <div className="flex flex-wrap items-center gap-2 rounded border border-gray-700 bg-gray-850 p-2">
      <ExprEditor expr={condition.left} indicators={indicators} onChange={(e) => onChange({ ...condition, left: e })} />
      <select
        className="rounded border border-gray-600 bg-gray-800 px-1.5 py-1 text-xs text-gray-200"
        value={condition.operator}
        onChange={(e) => onChange({ ...condition, operator: e.target.value as Operator })}
      >
        {OPERATORS.map((op) => <option key={op} value={op}>{op}</option>)}
      </select>
      <ExprEditor expr={condition.right} indicators={indicators} onChange={(e) => onChange({ ...condition, right: e })} />
      <button onClick={onRemove} className="ml-auto text-xs text-gray-600 hover:text-red-400">✕</button>
    </div>
  );
}
