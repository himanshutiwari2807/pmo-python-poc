from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

from app.config import settings
from app.db import Base
from app.models import Job  # noqa: F401  (registers the model on Base.metadata)

config = context.config

# Alembic runs migrations synchronously; swap the async aiomysql driver for
# the sync pymysql one just for this connection.
sync_url = settings.database_url.replace("mysql+aiomysql", "mysql+pymysql")
config.set_main_option("sqlalchemy.url", sync_url)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=target_metadata, literal_binds=True,
        dialect_opts={"paramstyle": "named"},
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
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
