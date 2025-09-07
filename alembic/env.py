import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Add the project's root directory to the Python path.
# This is crucial for Alembic to be able to find and import your
# application modules (like src.data_models) correctly.
sys.path.insert(0, os.path.abspath("."))

# Import the main SQLModel class.
from sqlmodel import SQLModel

# Your application's data models are imported here.
# Alembic's autogenerate feature will discover your tables through
# SQLModel's metadata, so it's important to import them.
from src import data_models

# This is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# This is the key part for SQLModel. We tell Alembic to use the
# metadata from the SQLModel class itself as the "target".
# This allows Alembic's autogenerate command to compare your models
# against the current database schema and create migration scripts.
target_metadata = SQLModel.metadata

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.
    
    This mode does not connect to the database. Instead, it generates SQL
    scripts that can be applied manually.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migration()

def run_migrations_online() -> None:
    """Run migrations in 'online' mode.
    
    This mode connects directly to the database and applies migrations.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )
        with context.begin_transaction():
            context.run_migration()

# Determine whether to run in online or offline mode and execute the migration.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
