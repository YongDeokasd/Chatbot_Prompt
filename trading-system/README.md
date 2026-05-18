# Trading System — Chart, Indicators & Backtesting (MVP)

Local-only trading analysis platform. See `../TODO_trading_system.md` for
the milestone checklist and the v1.1 report for full spec.

## Quick Start (target: 30 min to first chart)

```bash
cp .env.example .env
# put your ANTHROPIC_API_KEY in .env

docker build -t trading-sandbox:latest ./sandbox     # once
docker compose up -d
docker compose exec backend alembic upgrade head

# Frontend:        http://localhost:5173
# Backend Swagger: http://localhost:8000/docs
```

`LOCAL_API_TOKEN` is auto-generated into `.env` on first backend boot
(§8.1). The frontend reads it via `VITE_LOCAL_API_TOKEN`.

## Status

M1 (infra + chart) implemented. M2–M8 tracked in the to-do checklist.

## Conventions

- All timestamps UTC ISO 8601 (`...Z`); candles keyed by **open time** (§7).
- Dependency pins for pandas/numpy/numba/vectorbt/pandas-ta are exact (§4.1).
