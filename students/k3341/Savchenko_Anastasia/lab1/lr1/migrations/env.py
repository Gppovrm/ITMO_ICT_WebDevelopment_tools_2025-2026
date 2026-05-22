import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from logging.config import fileConfig
from sqlalchemy import engine_from_config
from sqlalchemy import pool
from alembic import context
from dotenv import load_dotenv
import os

# подгружаем переменные окружения из .env файла
load_dotenv()

# импортируем базовый класс моделей для автогенерации миграций
from app.models.models import Base

config = context.config

# берём url подключения из переменных окружения
database_url = os.getenv('DATABASE_URL')
if not database_url:
    raise ValueError("DATABASE_URL not set in environment variables")
config.set_main_option('sqlalchemy.url', database_url)


# настраиваем логирование из конфига alembic если он есть
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# указываем alembic на метаданные наших моделей по ним он будет отслеживать изменения и генерировать миграции
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """запуск миграций в офлайн режиме
    генерирует только sql скрипты без их выполнения"""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """запуск миграций в онлайн режиме
    создает реальное подключение к бд и выполняет миграции напрямую"""
    # создаем подключение к бд из конфига
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
            context.run_migrations()


# определяем режим запуска и выполняем соответствующие миграции
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()