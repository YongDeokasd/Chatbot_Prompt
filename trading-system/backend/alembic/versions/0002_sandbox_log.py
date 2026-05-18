"""sandbox_log table (§9.1)

Revision ID: 0002
Revises: 0001
"""
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        CREATE TABLE sandbox_log (
          id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
          indicator_id UUID,
          code_hash TEXT NOT NULL,
          duration_ms INTEGER NOT NULL,
          exit_code INTEGER NOT NULL,
          error TEXT,
          created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS sandbox_log")
