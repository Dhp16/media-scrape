import asyncio

from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import create_async_engine

from alembic import context

from manage_podcasts.db.models import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Helper function to run migrations within the async context."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        # Include other options like compare_type=True if needed
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    # Create an async engine
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"), # Get URL from alembic.ini
        poolclass=pool.NullPool, # Use NullPool for migrations
    )

    # Use the engine to connect, run migrations within a transaction
    async with connectable.connect() as connection:
        # Pass the helper function to run_sync
        await connection.run_sync(do_run_migrations)

    # Dispose the engine
    await connectable.dispose()

# Determine if running offline or online and execute
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Use asyncio.run to execute the async online migrations
    asyncio.run(run_migrations_online())