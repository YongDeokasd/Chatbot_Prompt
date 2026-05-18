# Trading System — Development To-Do Checklist

> Derived from `trading_system_report_v1.1.md` (TRADING-SYS-MVP).
> Senior-dev working checklist. Check items as development completes.
> Order follows milestone dependency graph: M1 → M2 → (M3→M4) / (M5→M6) / M7 → M8.

## Legend
- `[ ]` not started · `[~]` in progress · `[x]` done
- 🔴 = highest-risk / decision-gated item

---

## M0 — Pre-flight (decisions before code)

- [~] 🔴 Docker Socket Mount PoC plan agreed (code written; needs Docker host runtime verify)
- [x] 🔴 Signal evaluation contract §6.2 reviewed & signed off (implemented + regression tests pass)
- [~] 🔴 Pine whitelist scope §3.2 agreed (whitelist hardcoded in prompts.py; awaiting PM sign-off)
- [~] Confirm `fees_bps=10` / `slippage_bps=5` defaults (defaults coded; beta feedback needed)
- [x] Repo skeleton + branch protection + CHANGELOG.md created

## M1 — Infra + Chart (4d + 1d)

- [x] `docker-compose.yml` with backend, frontend, postgres, redis
- [x] FastAPI skeleton (`main.py`, `config.py`, `db.py`)
- [x] Alembic baseline migration (indicators, strategies, backtest_results, benchmark_symbols, candle_cache — §6.4)
- [x] `LOCAL_API_TOKEN` auto-generated on first boot (§8.1, §9.3)
- [x] `auth.py` — Bearer token middleware + Origin check (localhost/127.0.0.1)
- [x] `core/time.py` UTC helpers (ISO 8601 `Z`, §7)
- [x] Binance candle service (`services/market/binance.py`) + rate-limit/retry
- [x] `GET /api/market/candles` endpoint
- [x] Vite + React + TS + Tailwind scaffold
- [x] ChartPanel renders BTCUSDT 1h candles (lightweight-charts ≥4.1, indicator overlays, trade markers)
- [~] 🔴 **Docker Socket Mount PoC**: spawn code written (`services/indicators/sandbox.py`); needs Docker runtime verify <30s
- [~] **M1 DoD**: code complete; runtime verification pending Docker host

## M2 — Yahoo + Builtin Indicators + Availability Matrix (3d + 1d)

- [x] yfinance service + tz→UTC conversion (`services/market/yfinance_service.py`)
- [x] Timeframe availability matrix logic (§3.4) — per-source limits (`services/market/service.py`)
- [x] `GET /api/symbols/search`, `GET /api/symbols/{symbol}/timeframes`
- [x] `F-S5` resample service: yfinance 1h → 4h (`services/market/resample.py`) — tested
- [x] 7 builtin indicators via pandas-ta (SMA, EMA, RSI, MACD, BB, ATR, Volume)
- [x] `output_schema` populated for multi-line indicators (MACD/BB)
- [x] `POST /api/indicators/{id}/compute`
- [x] Frontend: SymbolSearch + TimeframeSelector (unavailable greyed out)
- [~] **M2 DoD**: code complete; runtime render verification pending Docker host

## M3 — Custom Indicators + Sandbox (4d + 2d)

- [x] Sandbox `Dockerfile` + `runner.py` + pinned `requirements.txt`
- [x] `services/indicators/validator.py` — AST import whitelist + banned patterns (§9.2) — 7 tests pass
- [x] `compute(candles, params)` signature enforcement
- [x] Container spawn flags: `--network none --memory 256m --cpus 0.5 --read-only --user nobody --pids-limit 50 --cap-drop ALL --rm`
- [x] 30s external timeout + auto-cleanup
- [x] Monaco editor integration (lazy load via `@monaco-editor/react`)
- [x] Sandbox execution log table (sandbox_log, migration 0002)
- [~] **M3 DoD**: code complete; sandbox runtime verify pending Docker host

## M4 — AI Pine Conversion + Whitelist (2d + 1d)

- [x] `core/prompts.py` + few-shot examples (RSI, MACD, BB)
- [x] Anthropic SDK integration; model from env; daily call limit; Redis cache (sha256 key, 24h TTL)
- [x] Whitelist enforcement: unsupported tokens → 422 + token list (§3.2)
- [x] `POST /api/ai/convert-pine` + PineImporter UI + warnings display
- [~] Regression tests: RSI(14), MACD(12,26,9), BB(20,2) vs TradingView ±0.1% (need live API key + TV export)
- [~] **M4 DoD**: regression tests need live Anthropic key + TradingView data; 422 path tested by whitelist unit

## M5 — Strategy Builder UI (3d + 1d)

- [x] Expression type model (indicator/constant/price + shift) — `schemas/strategy.py`
- [x] Condition/Operator schema (incl. cross_above/cross_below)
- [x] ConditionRow component + AND/OR combiner — `components/strategy/`
- [x] output_key selector UI (MACD macd/signal/hist)
- [x] `POST/GET/PUT/DELETE /api/strategies` + config_json persistence
- [~] **M5 DoD**: code complete; UI restore verification pending browser runtime

## M6 — Signal Evaluation + VectorBT (4d + 2d)

- [x] 🔴 `services/backtest/signal_evaluator.py` — §6.2 vectorized eval
- [x] Look-ahead guard: `shift(1)` enforced — 5 regression tests pass (cross_above, AND/OR, shift)
- [x] Position policy: Long-only, exit-priority on same bar
- [x] VectorBT `Portfolio.from_signals` adapter (imported inside function, not at startup)
- [x] Pull VectorBT stats (9 metrics) → `core/stats.py` formatting; persist to DB
- [x] Sync dispatch: ≤10k / ≤100k / >100k→422 (§5.2.2)
- [x] `POST /api/backtests/run`, `GET /api/backtests`, `GET /api/backtests/{id}`
- [x] Trade→Marker conversion (§6.3) + EquityCurve + TradeList UI
- [~] **M6 DoD**: code complete; VectorBT runtime perf test (<5s for 8760 candles) pending Docker host

## M7 — Realtime + Benchmark (2d + 1d)

- [x] `POST/GET/DELETE /api/benchmarks` CRUD
- [x] Binance WS streamer (`services/realtime/streamer.py`); yfinance 30s polling fallback
- [x] Redis pub/sub fan-out; `WS /api/ws/prices?token=...`
- [x] Redis AOF (`appendonly yes`, `appendfsync everysec`) + `redis_data` volume (docker-compose)
- [x] Frontend: BenchmarkPanel with live prices; 5s polling WS fallback (`lib/ws.ts`)
- [~] **M7 DoD**: code complete; live WS timing (<1s) pending Docker + Binance connectivity

## M8 — Finalize & Integration (2d + 2d)

- [x] Global 500 exception handler (structlog JSON, request_id in main.py)
- [x] README — 30-min quickstart
- [x] `app_logs` volume (docker-compose) + structlog JSON
- [ ] pg_dump daily cron + `./backups/` setup script (§14.4)
- [x] Unit test suite: validator (7), signal evaluator (5), time (5), resample (2) — 19/19 passing
- [x] Look-ahead bias regression tests pass (test_signal_evaluator.py)
- [ ] Playwright E2E suite (8 scenarios §13.3) — needs browser runtime
- [ ] 1-year backtest load test — needs VectorBT installed + Docker host
- [~] **M8 DoD**: unit tests green; E2E + load test pending runtime environment

---

## Cross-cutting (track throughout)

- [x] Version pins: pandas/numpy/numba/vectorbt/pandas-ta `==` (pyproject.toml)
- [x] All timestamps UTC ISO 8601, candles = open_time (§7) — enforced + tested
- [x] Pydantic validation at all boundaries; symbol regex; period limits; ≤100k candles (§9.4)
- [x] `.env.example` complete (§14.1); `.env` gitignored

## Open risks to revisit (§A.6)

- [~] Pine whitelist exact scope (hardcoded in prompts.py — PM sign-off needed pre-M4 DoD)
- [~] fees/slippage defaults suitability (defaults coded; beta feedback needed)
- [ ] 100k candle ceiling vs real usage (beta feedback)
- [~] Docker Socket Mount per-OS diffs (macOS/Linux/WSL2 — verify in M1 PoC on real host)
