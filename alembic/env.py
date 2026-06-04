from logging.config import fileConfig
import sys
import os
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Ensure the backend root directory is in the python path so 'app' can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.core.config import settings
from app.db.session import Base
# Import all models here so they register with Base.metadata
# This allows Alembic to detect your tables during 'autogenerate'
from app.models.user import User # noqa
from app.models.quiz import Quiz, Question, Option, QuizAttempt, AttemptAnswer # noqa
from app.models.lesson_completion import LessonCompletion # noqa
from app.models.certificate import Certificate # noqa

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Ensure database_url is a string and handle SQLAlchemy/Alembic requirements
database_url = str(settings.DATABASE_URL) if settings.DATABASE_URL else ""

# Fix protocol prefix for SQLAlchemy 1.4+
if database_url.startswith("postgres://"):
    database_url = database_url.replace("postgres://", "postgresql://", 1)

# Escape '%' for the Alembic ConfigParser to prevent interpolation errors
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

target_metadata = Base.metadata


def run_migrations_offline():
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    # Get the configuration section, defaulting to an empty dict if not found
    section = config.get_section(config.config_ini_section)
    alembic_config = dict(section) if section else {}

    # Ensure database_url is not empty before attempting to connect
    if not database_url:
        raise ValueError("DATABASE_URL is not set. Please check your .env file and application settings.")

    # Inject the corrected database URL directly into the configuration dictionary
    alembic_config["sqlalchemy.url"] = database_url

    connectable = engine_from_config(
        alembic_config,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
