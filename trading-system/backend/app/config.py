import secrets
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=str(ENV_PATH), extra="ignore")

    anthropic_api_key: str = ""
    anthropic_model: str = "claude-sonnet-4-20250514"
    anthropic_daily_call_limit: int = 200

    local_api_token: str = "auto_generated_on_first_boot"

    postgres_user: str = "trading"
    postgres_password: str = "trading"
    postgres_db: str = "trading"
    postgres_host: str = "postgres"
    postgres_port: int = 5432

    redis_host: str = "redis"
    redis_port: int = 6379

    sandbox_image: str = "trading-sandbox:latest"
    sandbox_timeout_sec: int = 30
    sandbox_memory: str = "256m"
    sandbox_cpus: str = "0.5"

    backtest_max_years: int = 5
    backtest_max_candles: int = 100000
    backtest_sync_timeout_sec: int = 30

    @property
    def database_url(self) -> str:
        return (
            f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}"
            f"@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    def ensure_local_token(self) -> str:
        """Generate LOCAL_API_TOKEN on first boot if not provided (§8.1)."""
        if self.local_api_token in ("", "auto_generated_on_first_boot"):
            token = secrets.token_hex(32)
            self.local_api_token = token
            try:
                lines = ENV_PATH.read_text().splitlines() if ENV_PATH.exists() else []
                out, found = [], False
                for line in lines:
                    if line.startswith("LOCAL_API_TOKEN="):
                        out.append(f"LOCAL_API_TOKEN={token}")
                        found = True
                    else:
                        out.append(line)
                if not found:
                    out.append(f"LOCAL_API_TOKEN={token}")
                ENV_PATH.write_text("\n".join(out) + "\n")
            except OSError:
                pass
        return self.local_api_token


settings = Settings()
