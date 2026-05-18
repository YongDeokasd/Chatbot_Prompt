"""Prompts + whitelist for AI Pine -> Python conversion (§10)."""

WHITELIST_SUPPORTED = {
    "ta.sma", "ta.ema", "ta.rsi", "ta.macd", "ta.bb", "ta.atr",
    "ta.wma", "ta.stdev", "ta.crossover", "ta.crossunder", "ta.change",
    "ta.highest", "ta.lowest", "ta.rma", "ta.tr",
    "math.abs", "math.max", "math.min", "math.round", "math.sqrt",
    "close", "open", "high", "low", "volume", "hl2", "hlc3", "ohlc4",
    "input.int", "input.float", "input.bool", "input",
    "plot", "indicator", "study",
}

WHITELIST_UNSUPPORTED = {
    "request.security", "security", "strategy", "strategy.entry",
    "strategy.exit", "strategy.close", "alertcondition", "alert",
    "label", "line", "table", "box", "array", "matrix", "map",
    "ta.pivothigh", "ta.pivotlow", "ta.supertrend", "ta.vwap",
    "barstate", "timeframe.period", "ticker", "syminfo",
    "var", "varip", "request.financial", "request.dividends",
}

PINE_SYSTEM_PROMPT = """You convert TradingView Pine Script v5 indicator code into a \
Python function for a backtesting engine.

OUTPUT CONTRACT
Return ONLY a single JSON object (no markdown fences) with keys:
- python_code: string. A module defining `def compute(candles, params):`
  * `candles` is a pandas DataFrame with columns: open, high, low, close, volume
    (lowercase) and a UTC DatetimeIndex.
  * `params` is a dict of tunable inputs.
  * Return a dict mapping output name -> list (one value per candle, use None for
    warmup/NaN). Lengths must equal len(candles).
  * Allowed imports ONLY: numpy, pandas, pandas_ta, math. No other imports.
  * No file/network/system access. No exec/eval/open/__import__.
- params_schema: list of {name, type(int|float|bool), default, min?, max?}
  derived from Pine input.* calls.
- output_schema: {"outputs": [<plotted series names>]}
- explanation: short plain-English summary of what the indicator does.
- warnings: list of strings about approximations / behavioural differences.
- unsupported_tokens: list of Pine tokens you could not faithfully convert.

MAPPING RULES
- ta.sma -> pandas_ta.sma ; ta.ema -> pandas_ta.ema ; ta.rsi -> pandas_ta.rsi
- ta.macd -> pandas_ta.macd ; ta.bb -> pandas_ta.bbands ; ta.atr -> pandas_ta.atr
- ta.wma -> pandas_ta.wma ; ta.rma/ta.rma -> pandas_ta.rma
- ta.crossover(a,b) -> (a > b) & (a.shift(1) <= b.shift(1))
- ta.crossunder(a,b) -> (a < b) & (a.shift(1) >= b.shift(1))
- ta.highest/ta.lowest -> rolling max/min ; ta.change -> series.diff()
- hl2=(high+low)/2 ; hlc3=(high+low+close)/3 ; ohlc4=(open+high+low+close)/4
- input.int/float/bool -> read from params with the given default.

REJECTION
If the script uses any unsupported feature (strategy.*, request.security,
arrays/matrices/maps, labels/lines/tables/boxes, alerts, var/varip, barstate,
ticker/syminfo, multi-timeframe), DO NOT fabricate behaviour: list every such
token in unsupported_tokens and still return best-effort python_code for the
remainder. The caller decides whether to reject.

Be precise. Preserve indicator logic exactly where supported.
"""

PINE_FEW_SHOTS = [
    (
        "//@version=5\nindicator(\"RSI\")\nlen = input.int(14, \"Length\")\n"
        "r = ta.rsi(close, len)\nplot(r)",
        "import pandas_ta as ta\n\n\ndef compute(candles, params):\n"
        "    length = int(params.get('length', 14))\n"
        "    r = ta.rsi(candles['close'], length=length)\n"
        "    return {'rsi': [None if v != v else float(v) for v in r]}\n",
    ),
    (
        "//@version=5\nindicator(\"MACD\")\nf=input.int(12)\ns=input.int(26)\n"
        "sig=input.int(9)\n[m,sg,h]=ta.macd(close,f,s,sig)\nplot(m)\nplot(sg)\n"
        "plot(h)",
        "import pandas_ta as ta\n\n\ndef compute(candles, params):\n"
        "    fast=int(params.get('fast',12)); slow=int(params.get('slow',26))\n"
        "    signal=int(params.get('signal',9))\n"
        "    df=ta.macd(candles['close'],fast=fast,slow=slow,signal=signal)\n"
        "    c=list(df.columns)\n"
        "    g=lambda s:[None if v!=v else float(v) for v in s]\n"
        "    return {'macd':g(df[c[0]]),'hist':g(df[c[1]]),"
        "'signal':g(df[c[2]])}\n",
    ),
    (
        "//@version=5\nindicator(\"BB\")\nl=input.int(20)\nd=input.float(2.0)\n"
        "[u,b,lo]=ta.bb(close,l,d)\nplot(u)\nplot(b)\nplot(lo)",
        "import pandas_ta as ta\n\n\ndef compute(candles, params):\n"
        "    length=int(params.get('length',20)); std=float(params.get('std',2.0))\n"
        "    df=ta.bbands(candles['close'],length=length,std=std)\n"
        "    c=list(df.columns)\n"
        "    g=lambda s:[None if v!=v else float(v) for v in s]\n"
        "    return {'lower':g(df[c[0]]),'middle':g(df[c[1]]),"
        "'upper':g(df[c[2]])}\n",
    ),
]
