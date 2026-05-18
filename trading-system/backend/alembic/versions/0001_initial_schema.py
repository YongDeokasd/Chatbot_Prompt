"""initial schema (§6.4)

Revision ID: 0001
Revises:
"""
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')
    op.execute(
        """
        CREATE TABLE indicators (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id TEXT NOT NULL DEFAULT 'local-user',
          name TEXT NOT NULL,
          code TEXT NOT NULL,
          language TEXT NOT NULL DEFAULT 'python',
          params_schema JSONB NOT NULL DEFAULT '[]',
          output_schema JSONB NOT NULL DEFAULT '{"outputs":["value"]}',
          is_builtin BOOLEAN NOT NULL DEFAULT false,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE strategies (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id TEXT NOT NULL DEFAULT 'local-user',
          name TEXT NOT NULL,
          symbol TEXT NOT NULL,
          exchange TEXT NOT NULL,
          timeframe TEXT NOT NULL,
          position_type TEXT NOT NULL DEFAULT 'long',
          fees_bps NUMERIC NOT NULL DEFAULT 10,
          slippage_bps NUMERIC NOT NULL DEFAULT 5,
          initial_cash NUMERIC NOT NULL DEFAULT 10000,
          config_json JSONB NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE backtest_results (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          strategy_id UUID NOT NULL REFERENCES strategies(id) ON DELETE CASCADE,
          period_from TIMESTAMPTZ NOT NULL,
          period_to TIMESTAMPTZ NOT NULL,
          stats_json JSONB NOT NULL,
          trades_json JSONB NOT NULL,
          equity_curve_json JSONB NOT NULL,
          duration_ms INTEGER NOT NULL,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );

        CREATE TABLE benchmark_symbols (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          user_id TEXT NOT NULL DEFAULT 'local-user',
          symbol TEXT NOT NULL,
          exchange TEXT NOT NULL,
          active BOOLEAN NOT NULL DEFAULT true,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
          UNIQUE (user_id, symbol, exchange)
        );

        CREATE TABLE candle_cache (
          symbol TEXT NOT NULL,
          exchange TEXT NOT NULL,
          timeframe TEXT NOT NULL,
          open_time TIMESTAMPTZ NOT NULL,
          open NUMERIC NOT NULL, high NUMERIC NOT NULL,
          low NUMERIC NOT NULL, close NUMERIC NOT NULL,
          volume NUMERIC NOT NULL,
          PRIMARY KEY (symbol, exchange, timeframe, open_time)
        );
        CREATE INDEX idx_candle_cache_lookup
          ON candle_cache (symbol, exchange, timeframe, open_time DESC);
        """
    )


def downgrade() -> None:
    op.execute(
        "DROP TABLE IF EXISTS candle_cache, backtest_results, "
        "benchmark_symbols, strategies, indicators CASCADE"
    )
