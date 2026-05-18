# Changelog

## [Unreleased] — M1–M8 code complete

### M1 — Infra + Chart
- Docker Compose stack (backend, frontend, postgres, redis with AOF), named volumes
- FastAPI skeleton: config, db, UTC time helpers, local token auth, /health, structlog
- Alembic baseline migration (§6.4 schema: indicators, strategies, backtest_results, benchmark_symbols, candle_cache)
- Binance candle service + `GET /api/market/candles`
- Vite + React + TS + Tailwind chart UI (lightweight-charts v4, BTCUSDT 1h, indicator overlays, trade markers)
- Sandbox image + runner.py + Docker Socket Mount spawn service

### M2 — Yahoo + Builtin Indicators + Availability Matrix
- yfinance service with tz→UTC conversion (§7)
- Timeframe availability matrix with per-source limits (§3.4)
- Resample service: 1h → 4h (§F-S5), tested
- `GET /api/symbols/search`, `GET /api/symbols/{symbol}/timeframes`
- 7 builtin indicators via pandas-ta (SMA, EMA, RSI, MACD, BB, ATR, Volume) with output_schema
- `POST /api/indicators/{id}/compute` + full indicator CRUD
- Frontend: SymbolSearch + TimeframeSelector with availability gating

### M3 — Custom Indicators + Sandbox
- AST-based code validator: import whitelist + banned call patterns (§9.2)
- sandbox_log DB table (migration 0002)
- Monaco editor (lazy-loaded) for custom indicator editing
- IndicatorEditor + IndicatorList components

### M4 — AI Pine → Python Conversion
- Anthropic SDK integration with few-shot prompts (RSI, MACD, BB)
- Pine whitelist + unsupported-token 422 rejection (§3.2)
- Redis cache (sha256, 24h TTL) + daily call limit counter
- `POST /api/ai/convert-pine` + PineImporter UI + warnings display

### M5 — Strategy Builder
- Expression/Condition/Operator schema (§6.1): indicator, price, constant + shift
- ConditionRow UI with output_key selector (MACD macd/signal/hist)
- AND/OR logic combiner
- Full strategy CRUD `POST/GET/PUT/DELETE /api/strategies`

### M6 — Signal Evaluation + VectorBT
- Vectorized signal evaluator (§6.2): cross_above/cross_below, shift(1) look-ahead guard
- Long-only position policy, exit-priority on same bar (§6.2.3)
- VectorBT Portfolio.from_signals adapter (lazy import, bps→ratio)
- 9-metric stats formatting + DB persistence
- Candle count dispatch: ≤10k/≤100k/422>100k (§5.2.2)
- Backtest CRUD + Trade→Marker (§6.3) + EquityCurve + TradeList UI

### M7 — Realtime + Benchmark
- Benchmark CRUD `POST/GET/DELETE /api/benchmarks`
- Binance WebSocket streamer + yfinance 30s polling fallback
- Redis pub/sub fan-out + `WS /api/ws/prices?token=...`
- BenchmarkPanel with live price display + 5s polling WS fallback

### M8 — Tests & Integration
- 19 unit tests passing: validator (7), signal evaluator (5), time (5), resample (2)
- Look-ahead bias regression suite (test_signal_evaluator.py)
- Global 500 handler + structlog JSON + app_logs volume
- README 30-min quickstart
