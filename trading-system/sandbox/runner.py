"""Sandbox entrypoint. Reads {code, candles_json, params} from stdin,
executes compute() in a restricted namespace, writes result JSON to stdout.

Full static validation happens backend-side (M3, §9.2). This is the
M1 PoC runner proving Docker Socket Mount spawn works end-to-end.
"""
import json
import sys

import pandas as pd

ALLOWED_BUILTINS = {"len", "range", "min", "max", "abs", "sum", "float", "int"}


def main() -> None:
    payload = json.loads(sys.stdin.read())
    code = payload["code"]
    candles = pd.DataFrame(payload.get("candles_json", []))
    params = payload.get("params", {})

    safe_builtins = {k: __builtins__[k] for k in ALLOWED_BUILTINS if k in __builtins__} \
        if isinstance(__builtins__, dict) else \
        {k: getattr(__builtins__, k) for k in ALLOWED_BUILTINS if hasattr(__builtins__, k)}

    ns: dict = {"pd": pd, "__builtins__": safe_builtins}
    exec(code, ns)  # noqa: S102 — sandboxed container, validated upstream
    result = ns["compute"](candles, params)

    if isinstance(result, pd.Series):
        out = {"value": result.fillna(0).tolist()}
    else:
        out = {k: v.fillna(0).tolist() for k, v in result.items()}

    sys.stdout.write(json.dumps({"ok": True, "outputs": out}))


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:  # noqa: BLE001
        sys.stdout.write(json.dumps({"ok": False, "error": str(exc)}))
        sys.exit(1)
