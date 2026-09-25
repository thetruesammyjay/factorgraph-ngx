"""Alembic environment configured against the API SQLAlchemy metadata."""

import sys
from pathlib import Path

from sqlalchemy import engine_from_config, pool

from alembic import context

# Make the API package importable when Alembic is launched from its console script.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.config import settings
from app.db.session import sqlalchemy_database_url
from app.db.models import Base

config = context.config

if not settings.database_url:
    raise RuntimeError("DATABASE_URL must be configured before running migrations")

# Alembic uses percent interpolation in its config parser. Escaping percent
# characters keeps passwords containing '%' valid.
database_url = sqlalchemy_database_url(settings.database_url)
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata, compare_type=True)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
