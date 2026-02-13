import os
import sys
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Ensure Backend/ is on sys.path so "from config.database" works
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from config.database import Base, DATABASE_URL

# Import ALL models so Base.metadata sees them
from models.employees import Employees  # noqa
from models.clients import Client  # noqa
from models.projects import Project  # noqa
from models.time_entries import TimeEntry  # noqa
from models.assigned_projects import AssignedProject  # noqa
from models.invoice import Invoice  # noqa
from models.invoice_lines import InvoiceLine  # noqa
from models.weeks import Week  # noqa
from models.app_user import AppUser  # noqa

config = context.config

# Override sqlalchemy.url from env var if available
config.set_main_option("sqlalchemy.url", DATABASE_URL)

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(url=url, target_metadata=target_metadata, literal_binds=True)
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
