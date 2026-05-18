# Trading System — Development To-Do Checklist

> Derived from `trading_system_report_v1.1.md` (TRADING-SYS-MVP).
> Senior-dev working checklist. Check items as development completes.
> Order follows milestone dependency graph: M1 → M2 → (M3→M4) / (M5→M6) / M7 → M8.

## Legend
- `[ ]` not started · `[~]` in progress · `[x]` done
- 🔴 = highest-risk / decision-gated item

---

## M0 — Pre-flight (decisions before code)

- [ ] 🔴 Docker Socket Mount PoC plan agreed (decision before M1 end, §1.3)
- [ ] 🔴 Signal evaluation contract §6.2 reviewed & signed off (before M5)
- [ ] 🔴 Pine whitelist scope §3.2 agreed (before M4)
- [ ] Confirm `fees_bps=10` / `slippage_bps=5` defaults (Crypto vs Stocks, §A.6)
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
- [x] Vite + React + TS + Tailwind scaffold (shadcn/ui deferred to M2 UI work)
- [x] ChartPanel renders BTCUSDT 1h candles (lightweight-charts ≥4.1)
- [~] 🔴 **Docker Socket Mount PoC**: spawn code written (`services/indicators/sandbox.py`); needs Docker runtime to verify <30s end-to-end
- [~] **M1 DoD**: code complete; runtime verification (`docker-compose up`, `/health` 200, chart, PoC) pending a Docker host

## M2 — Yahoo + Builtin Indicators + Availability Matrix (3d + 1d)

- [ ] yfinance service + tz→UTC conversion (§7)
- [ ] Timeframe availability matrix logic (§3.4) — per-source limits
- [ ] `GET /api/symbols/search`, `GET /api/symbols/{symbol}/timeframes`
- [ ] `F-S5` resample service: yfinance 1h → 4h
- [ ] 7 builtin indicators via pandas-ta (SMA, EMA, RSI, MACD, BB, ATR, Volume)
- [ ] `output_schema` populated for multi-line indicators (MACD/BB)
- [ ] `POST /api/indicators/{id}/compute`
- [ ] Frontend: unavailable timeframes greyed out per symbol
- [ ] **M2 DoD**: AAPL & ^GSPC chart; gating works; MACD/BB multi-line render

## M3 — Custom Indicators + Sandbox (4d + 2d)

- [ ] Sandbox `Dockerfile` + `runner.py` + pinned `requirements.txt`
- [ ] `services/indicators/validator.py` — AST import whitelist + banned patterns (§9.2)
- [ ] `compute(candles, params)` signature enforcement; no in-place mutation
- [ ] Container spawn flags: `--network none --memory 256m --cpus 0.5 --read-only --user nobody --pids-limit 50 --cap-drop ALL --rm` (§9.1)
- [ ] 30s external timeout + auto-cleanup
- [ ] Monaco editor integration (lazy load)
- [ ] Sandbox execution log table (code hash, time, mem peak, exit code, §14.3)
- [ ] **M3 DoD**: SMA-variant overlay; infinite loop killed <30s; banned import rejected at save; 256m OOM → error response

## M4 — AI Pine Conversion + Whitelist (2d + 1d)

- [ ] `core/prompts.py` + few-shot for Pine→Python
- [ ] Anthropic SDK integration; model from `ANTHROPIC_MODEL`; daily call limit
- [ ] Whitelist enforcement: unsupported tokens → 422 + token list (§3.2)
- [ ] Redis cache for conversion results
- [ ] `POST /api/ai/convert-pine` + PineImporter UI + warnings display
- [ ] Regression tests: RSI(14), MACD(12,26,9), BB(20,2) vs TradingView ±0.1%
- [ ] **M4 DoD**: 3 conversions ±0.1%; `request.security` → 422; warnings shown

## M5 — Strategy Builder UI (3d + 1d, parallel after M2)

- [ ] Expression type model (indicator/constant/price + shift) — §6.1
- [ ] Condition/Operator schema (incl. cross_above/cross_below)
- [ ] ConditionRow component + AND/OR combiner
- [ ] output_key selector UI (e.g. MACD macd/signal/hist)
- [ ] `POST/GET/PUT/DELETE /api/strategies` + config_json persistence
- [ ] **M5 DoD**: 2+ indicator AND/OR strategy saved; strategy reload fully restores UI

## M6 — Signal Evaluation + VectorBT (4d + 2d)

- [ ] 🔴 `services/backtest/signal_evaluator.py` — §6.2 vectorized eval
- [ ] Look-ahead guard: eval on bar close, fill at next bar open, `shift(1)` (§6.2.4)
- [ ] Position policy: Long-only, 1 pos, exit-priority on same bar (§6.2.3)
- [ ] VectorBT `Portfolio.from_signals` adapter; fees/slippage bps→ratio
- [ ] Pull VectorBT stats (9 metrics) → persist; `core/stats.py` formatting only
- [ ] Sync/async dispatch: ≤10k 10s SLA / ≤100k 30s SLA / >100k → 422 (§5.2.2)
- [ ] `POST /api/backtests/run`, `GET /api/backtests`, `GET /api/backtests/{id}`
- [ ] Trade→Marker conversion (§6.3) + EquityCurve + TradeList UI
- [ ] **M6 DoD**: 1y 1h (~8760) <5s; look-ahead regression passes; 9 stats shown; markers+curve+list render

## M7 — Realtime + Benchmark (2d + 1d, parallel after M1)

- [ ] `POST/GET/DELETE /api/benchmarks` CRUD
- [ ] Binance WS streamer; yfinance 30s polling fallback
- [ ] Redis cache + pub/sub fan-out; `WS /api/ws/prices` (token via querystring)
- [ ] Redis AOF (`appendonly yes`, `appendfsync everysec`) + `redis_data` volume
- [ ] Frontend: last-candle live update; 5s polling on WS drop
- [ ] **M7 DoD**: <1s WS price flow; polling fallback keeps chart; cache survives reboot

## M8 — Finalize & Integration (2d + 2d)

- [ ] Global error handling + friendly messages (incl. yfinance availability, API down 503)
- [ ] README — new dev local run in 30 min
- [ ] `app_logs` volume + structlog JSON + request_id (§14.3)
- [ ] pg_dump daily cron + `./backups/` (§14.4)
- [ ] E2E suite (8 scenarios, §13.3) automated via Playwright
- [ ] Look-ahead bias regression in CI
- [ ] 1-year backtest load test (<5s; 3 concurrent no memory blowup; 5-symbol WS 1h)
- [ ] **M8 DoD**: all of the above green

---

## Cross-cutting (track throughout)

- [ ] Version pins: pandas/numpy/numba/vectorbt/pandas-ta `==` (§4.1, §17.1)
- [ ] CI: VectorBT/Numba import smoke test
- [ ] All timestamps UTC ISO 8601, candles = open_time (§7)
- [ ] Pydantic validation at all boundaries; symbol regex; period 1d–5y; ≤100k candles (§9.4)
- [ ] `.env.example` complete (§14.1); secrets gitignored

## Open risks to revisit (§A.6)

- [ ] Pine whitelist exact scope (pre-M4)
- [ ] fees/slippage defaults suitability
- [ ] 100k candle ceiling vs real usage (beta feedback)
- [ ] Docker Socket Mount per-OS diffs (macOS/Linux/WSL2 — verify in M1 PoC)
