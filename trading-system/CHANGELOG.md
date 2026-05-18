# Changelog

## [Unreleased]

### M1 — Infra + Chart (in progress)
- Docker Compose stack (backend, frontend, postgres, redis with AOF)
- FastAPI skeleton: config, db, UTC time helpers, local token auth, /health
- Alembic baseline migration for §6.4 schema
- Binance candle service + `GET /api/market/candles`
- Vite + React + TS + Tailwind chart UI (lightweight-charts, BTCUSDT 1h)
- Sandbox image + runner.py + Docker Socket Mount spawn (PoC)
