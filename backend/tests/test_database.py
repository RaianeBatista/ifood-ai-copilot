from sqlalchemy.engine import make_url

from app.database import _normalize_database_url


def test_postgresql_url_uses_installed_psycopg_driver():
    database_url = _normalize_database_url(
        "postgresql://user:password@localhost:5432/copilot"
    )

    assert database_url.get_backend_name() == "postgresql"
    assert database_url.get_driver_name() == "psycopg"


def test_legacy_postgres_scheme_uses_installed_psycopg_driver():
    database_url = _normalize_database_url(
        "postgres://user:password@localhost:5432/copilot"
    )

    assert database_url.get_backend_name() == "postgresql"
    assert database_url.get_driver_name() == "psycopg"


def test_sqlite_url_is_preserved():
    database_url = _normalize_database_url("sqlite:///test.db")

    assert database_url == make_url("sqlite:///test.db")
