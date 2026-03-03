from __future__ import annotations

import pytest

from db import ENSURE_EMPLOYEE_EMPID_UNIQUE_INDEX_SQL, UPSERT_EMPLOYEE_SQL
from settings import ConfigurationError, DatabaseConfig


def test_database_config_defaults(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("EMP_DB_DSN", raising=False)
    monkeypatch.delenv("EMP_DB_HOST", raising=False)
    monkeypatch.delenv("EMP_DB_PORT", raising=False)
    monkeypatch.delenv("EMP_DB_NAME", raising=False)
    monkeypatch.delenv("EMP_DB_USER", raising=False)
    monkeypatch.delenv("EMP_DB_PASSWORD", raising=False)
    monkeypatch.delenv("EMP_DB_CONNECT_TIMEOUT", raising=False)

    config = DatabaseConfig.from_env(load_env_file=False)

    assert config.dsn is None
    assert config.host == "localhost"
    assert config.port == 5432
    assert config.dbname == "employee_management"
    assert config.user == "postgres"
    assert config.password == "postgres"
    assert config.connect_timeout == 5


def test_database_config_from_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMP_DB_DSN", "postgresql://user:pass@localhost:5432/app")
    monkeypatch.setenv("EMP_DB_HOST", "dbhost")
    monkeypatch.setenv("EMP_DB_PORT", "5433")
    monkeypatch.setenv("EMP_DB_NAME", "appdb")
    monkeypatch.setenv("EMP_DB_USER", "appuser")
    monkeypatch.setenv("EMP_DB_PASSWORD", "secret")
    monkeypatch.setenv("EMP_DB_CONNECT_TIMEOUT", "10")

    config = DatabaseConfig.from_env()

    assert config.dsn == "postgresql://user:pass@localhost:5432/app"
    assert config.host == "dbhost"
    assert config.port == 5433
    assert config.dbname == "appdb"
    assert config.user == "appuser"
    assert config.password == "secret"
    assert config.connect_timeout == 10


def test_database_config_invalid_port(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("EMP_DB_PORT", "invalid")

    with pytest.raises(ConfigurationError, match="EMP_DB_PORT must be an integer"):
        DatabaseConfig.from_env()


def test_upsert_query_uses_conflict_on_empid() -> None:
    assert "ON CONFLICT (empid) DO UPDATE" in UPSERT_EMPLOYEE_SQL


def test_unique_index_sql_targets_empid() -> None:
    assert "CREATE UNIQUE INDEX IF NOT EXISTS" in ENSURE_EMPLOYEE_EMPID_UNIQUE_INDEX_SQL
    assert "ON employees (empid)" in ENSURE_EMPLOYEE_EMPID_UNIQUE_INDEX_SQL
