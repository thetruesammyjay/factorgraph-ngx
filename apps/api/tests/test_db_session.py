from app.db.session import sqlalchemy_database_url


def test_standard_postgresql_urls_use_psycopg_three():
    assert sqlalchemy_database_url("postgresql://user:pass@host/db") == (
        "postgresql+psycopg://user:pass@host/db"
    )
    assert sqlalchemy_database_url("postgres://user:pass@host/db") == (
        "postgresql+psycopg://user:pass@host/db"
    )


def test_explicit_sqlalchemy_driver_is_preserved():
    url = "postgresql+psycopg://user:pass@host/db"
    assert sqlalchemy_database_url(url) == url
