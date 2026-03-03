"""Application configuration and environment loading."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_ENV_FILE = Path(__file__).resolve().parents[1] / ".env"


class ConfigurationError(ValueError):
    """Raised when environment configuration is invalid."""


def load_environment(env_file: Path | None = None) -> None:
    """Load variables from .env into process environment if present."""
    load_dotenv(dotenv_path=env_file or DEFAULT_ENV_FILE, override=False)


def parse_int_env(var_name: str, default: int) -> int:
    raw_value = os.getenv(var_name)
    if raw_value is None:
        return default

    try:
        return int(raw_value)
    except ValueError as exc:
        raise ConfigurationError(f"{var_name} must be an integer") from exc


@dataclass(frozen=True)
class DatabaseConfig:
    """Database configuration sourced from environment variables."""

    dsn: str | None
    host: str
    port: int
    dbname: str
    user: str
    password: str
    connect_timeout: int

    @classmethod
    def from_env(cls, load_env_file: bool = True) -> DatabaseConfig:
        if load_env_file:
            load_environment()
        dsn = os.getenv("EMP_DB_DSN") or None
        return cls(
            dsn=dsn,
            host=os.getenv("EMP_DB_HOST", "localhost"),
            port=parse_int_env("EMP_DB_PORT", 5432),
            dbname=os.getenv("EMP_DB_NAME", "employee_management"),
            user=os.getenv("EMP_DB_USER", "postgres"),
            password=os.getenv("EMP_DB_PASSWORD", "postgres"),
            connect_timeout=parse_int_env("EMP_DB_CONNECT_TIMEOUT", 5),
        )
