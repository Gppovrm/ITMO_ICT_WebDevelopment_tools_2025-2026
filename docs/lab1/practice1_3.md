# Отчет по практической работе №1.3

**Тема:** Миграции, ENV, GitIgnore и структура проекта

## 🎯 Цель работы

Научиться правильно структурировать FastAPI проект, использовать переменные окружения для хранения конфиденциальных
данных, настраивать миграции через Alembic и исключать служебные файлы из Git с помощью `.gitignore`.

---

## 📋 Условия выполнения

Работа выполнялась в рамках лабораторной работы №1 по пути:  
`students\k3341\Savchenko_Anastasia\lab1\pr_3`

**Стек технологий:**

- Python 3.10+
- FastAPI
- SQLModel
- PostgreSQL
- Alembic (миграции)
- python-dotenv (переменные окружения)

---

## 🗂️ 1. Структура проекта

В ходе работы была создана следующая структура проекта:

```

pr_3/
├── app/ # Основной модуль приложения
│ ├── __init__.py # Маркер пакета Python
│ ├── database.py # Подключение к БД
│ ├── models.py # SQLModel модели
│ ├── main.py # FastAPI приложение
│ └── routers/ # Роутеры (разделение эндпоинтов)
│ ├── __init__.py
│ ├── warriors.py # CRUD для воинов
│ ├── professions.py # CRUD для профессий
│ └── skills.py # CRUD для умений
├── migrations/ # Миграции Alembic
│ ├── versions/ # Файлы миграций
│ ├── env.py # Настройки окружения
│ └── script.py.mako # Шаблон миграций
├── .env # Переменные окружения (НЕ в Git)
├── .gitignore # Исключения для Git
├── alembic.ini # Конфигурация Alembic
└── venv/ # Виртуальное окружение

```

---

## 🔐 2. Переменные окружения (.env)

### Создание файла `.env`

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/warriors_db
```

### Использование в `database.py`

``` python
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
engine = create_engine(DATABASE_URL, echo=True)


def init_db():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
```

### Зачем это нужно?

- Пароли и ключи не хранятся в коде
- Разные окружения (dev/prod) используют разные настройки
- Безопасность при публикации на GitHub

---

## 🔄 3. Миграции Alembic

### Установка и инициализация

``` bash
pip install alembic
alembic init migrations
```

### Настройка `alembic.ini`

``` ini
sqlalchemy.url = postgresql://postgres:postgres@localhost:5432/warriors_db
```

### Настройка `migrations/env.py`

``` python
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from app.models import SQLModel
from dotenv import load_dotenv
import os

load_dotenv()

target_metadata = SQLModel.metadata
config.set_main_option('sqlalchemy.url', os.getenv('DATABASE_URL'))
```

### Создание и применение миграции

``` bash
# Создать миграцию
alembic revision --autogenerate -m "initial_migration"

# Применить миграцию
alembic upgrade head
```

### Результат выполнения

```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> d838187a161e, initial_migration
```

---

## 📁 4. Разделение кода на роутеры

### `app/routers/__init__.py`

``` python
from .warriors import router as warriors_router
from .professions import router as professions_router
from .skills import router as skills_router
```

### `app/routers/warriors.py` (пример)

``` python
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from app.database import get_session
from app.models import Warrior, WarriorDefault, WarriorProfessions

router = APIRouter(prefix='/warriors', tags=['Warriors'])


@router.get('/', response_model=List[WarriorProfessions])
def get_warriors(session=Depends(get_session)):
    return session.exec(select(Warrior)).all()


@router.post('/')
def create_warrior(warrior: WarriorDefault, session=Depends(get_session)):
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return {'status': 200, 'data': db_warrior}
```

### `app/main.py` (подключение роутеров)

``` python
from fastapi import FastAPI
from app.database import init_db
from app.routers import warriors_router, professions_router, skills_router

app = FastAPI(title='FastAPI Warriors API', version='1.0.0')


@app.on_event('startup')
def on_startup():
    init_db()


app.include_router(warriors_router)
app.include_router(professions_router)
app.include_router(skills_router)
```

---

## 🚀 5. Запуск приложения

``` bash
uvicorn app.main:app --reload
```

**Результат:**

```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

---

## 📊 6. Итоговые эндпоинты

| Группа      | Эндпоинты                   | Методы                   |
|-------------|-----------------------------|--------------------------|
| Warriors    | `/warriors/`                | GET, POST, PATCH, DELETE |
| Warriors    | `/warriors/{id}/skill/{id}` | POST                     |
| Professions | `/professions/`             | GET, POST, PATCH, DELETE |
| Skills      | `/skills/`                  | GET, POST, PATCH, DELETE |

Документация доступна по адресу: http://127.0.0.1:8000/docs

---

## 🔍 Анализ выполненной работы

В ходе выполнения практической работы были реализованы следующие задачи: создана правильная структура FastAPI проекта с
разделением на модули и роутеры, настроены переменные окружения через `.env` для безопасного хранения пароля от базы
данных, создан `.gitignore` для исключения служебных файлов (виртуальное окружение, `.env`, кэш) из Git, установлен и
настроен Alembic для управления миграциями, создана и успешно применена миграция "initial_migration" для создания всех
таблиц в PostgreSQL.

В результате были получены практические навыки: организация модульной структуры FastAPI приложения, безопасное хранение
конфиденциальных данных через `.env`, работа с Git (правильное составление `.gitignore`), создание и применение миграций
через Alembic, разделение эндпоинтов на роутеры с подключением их в `main.py`.

## Выводы

Практическая работа №1.3 успешно выполнена. Реализованы все ключевые улучшения: код разделён на логические модули, что
упрощает поддержку проекта; пароли вынесены в `.env` и исключены из Git через `.gitignore`, что обеспечивает
безопасность; настроен Alembic для управления изменениями в схеме базы данных. Автоматическая документация Swagger
отображает все эндпоинты, сгруппированные по тегам. Работа подтвердила, что правильная организация проекта является
основой для разработки поддерживаемых и безопасных веб-приложений на FastAPI.