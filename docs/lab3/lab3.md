# Отчет по лабораторной работе №3

## Упаковка FastAPI приложения в Docker, работа с источниками данных и очередями

---

**Дисциплина:** Web-программирование
**Студент:** Савченко Анастасия Сергеевна
**Группа:** K3341
**Поток:** WEB 2.3

---

## Цель работы

Научиться упаковывать FastAPI приложение в Docker, интегрировать парсер данных с базой данных и вызывать парсер через API и очередь.

---

## Выполнение работы

### Подзадача 1: Упаковка FastAPI приложения, базы данных и парсера данных в Docker

#### 1.1. Что было из прошлых работ

| Компонент          | Откуда                 | Описание                                                                              |
| ------------------ | ---------------------- | ------------------------------------------------------------------------------------- |
| FastAPI приложение | Лабораторная работа №1 | Тайм-менеджер с авторизацией, проектами, задачами (6 таблиц)                          |
| База данных        | Лабораторная работа №1 | PostgreSQL с таблицами users, projects, tasks, time_logs, categories, task_categories |
| Парсер данных      | Лабораторная работа №2 | Парсинг книг с Project Gutenberg (название, автор, ID)                                |

#### 1.2. Dockerfile для основного приложения

**Файл:** `Dockerfile`

``` dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
COPY celery_requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir -r celery_requirements.txt

COPY . .

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Что делает этот Dockerfile:**

* Базовый образ `python:3.10-slim` — лёгкий, без лишних пакетов.
* Устанавливает зависимости для основного приложения и Celery.
* Копирует весь код проекта.
* Запускает uvicorn-сервер на порту 8000.

#### 1.3. Dockerfile для парсера

**Файл:** `parser/Dockerfile`

``` dockerfile
FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD ["uvicorn", "parser_api:app", "--host", "0.0.0.0", "--port", "8001"]
```

**Что делает этот Dockerfile:**

* Собирает отдельный микросервис парсера.
* Запускается на порту 8001.
* Независим от основного приложения.

#### 1.4. Docker Compose

**Файл:** `docker-compose.yml`

``` yaml
services:
  db:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
      POSTGRES_DB: timemanager_db
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  redis:
    image: redis:7
    ports:
      - "6379:6379"

  parser:
    build: ./parser
    ports:
      - "8001:8001"
    volumes:
      - ./parser:/app
    command: uvicorn parser_api:app --host 0.0.0.0 --port 8001 --reload

  app:
    build: .
    depends_on:
      - db
      - parser
      - redis
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/timemanager_db
      JWT_SECRET: your-super-secret-key-change-me
      JWT_ALGORITHM: HS256
      JWT_EXPIRE_MINUTES: 60
    ports:
      - "8000:8000"
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  celery_worker:
    build: .
    depends_on:
      - redis
      - parser
    environment:
      DATABASE_URL: postgresql://postgres:postgres@db:5432/timemanager_db
    volumes:
      - .:/app
    command: celery -A celery_app worker --loglevel=info

volumes:
  postgres_data:
```

**Сервисы в `docker-compose.yml`:**

| Сервис        | Назначение                   | Порт |
| ------------- | ---------------------------- | ---- |
| db            | PostgreSQL — хранение данных | 5432 |
| redis         | Брокер сообщений для Celery  | 6379 |
| parser        | Микросервис парсера          | 8001 |
| app           | Основное FastAPI приложение  | 8000 |
| celery_worker | Воркер для асинхронных задач | —    |

**Зависимости между сервисами:**

* `app` зависит от `db`, `parser`, `redis`;
* `celery_worker` зависит от `redis`, `parser`.

---

### Подзадача 2: Вызов парсера из FastAPI (синхронно)

#### 2.1. Эндпоинт `/parse-url`

Я добавила в `app/main.py` следующий эндпоинт:

``` python
@app.post("/parse-url")
async def parse_url(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://parser:8001/parse",
            params={"url": url}
        )
    return response.json()
```

**Как это работает:**

1. Клиент отправляет POST-запрос с URL.
2. FastAPI приложение отправляет запрос к контейнеру парсера по адресу `parser:8001`.
3. Парсер парсит страницу и возвращает данные.
4. FastAPI возвращает результат клиенту.

**Пример запроса и ответа:**

``` json
POST /parse-url?url=https://www.gutenberg.org/ebooks/84

{
  "url": "https://www.gutenberg.org/ebooks/84",
  "title": "Frankenstein; or, the modern prometheus",
  "author": "Shelley",
  "gutenberg_id": 84
}
```

---

### Подзадача 3: Асинхронный вызов через очередь (Celery + Redis)

#### 3.1. Что такое Celery и Redis

**Celery** — библиотека для асинхронной обработки задач. Позволяет выполнять длительные операции в фоне, не блокируя основной поток приложения.

**Redis** — база данных в памяти, которая используется как брокер сообщений. Хранит очередь задач и результаты их выполнения.

#### 3.2. Как это работает в моём проекте

``` text
Клиент → POST /parse-url-async → FastAPI → Redis (очередь) → Celery Worker → парсинг → Redis (результат)
                                              ↓
                                        Клиент получает task_id
                                              ↓
                                  GET /task-result/{task_id} → результат
```

#### 3.3. Конфигурация Celery

**Файл:** `celery_app.py`

``` python
from celery import Celery
from parser import parse_gutenberg_book

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

@celery_app.task(name="parse_url_task")
def parse_url_task(url: str):
    return parse_gutenberg_book(url)
```

**Что здесь настроено:**

* Брокер (`broker`) — Redis на порту 6379.
* Бэкенд (`backend`) — Redis для хранения результатов.
* Задача `parse_url_task` — вызывает функцию парсинга из ЛР №2.

#### 3.4. Асинхронные эндпоинты

**Эндпоинт для отправки задачи:**

``` python
@app.post("/parse-url-async")
def parse_url_async(url: str):
    task = celery_app.send_task("parse_url_task", args=[url])
    return {"task_id": task.id, "status": "queued"}
```

**Эндпоинт для получения результата:**

``` python
from celery.result import AsyncResult

@app.get("/task-result/{task_id}")
def get_task_result(task_id: str):
    task = AsyncResult(task_id, app=celery_app)

    if task.ready():
        return {
            "task_id": task_id,
            "status": "completed",
            "result": task.result
        }
    else:
        return {
            "task_id": task_id,
            "status": "pending"
        }
```

#### 3.5. Тестирование асинхронного подхода

**Шаг 1 — отправка задачи:**

``` json
POST /parse-url-async?url=https://www.gutenberg.org/ebooks/84

{
  "task_id": "2d7c72d9-6e28-43d8-88d7-7ca3f151e1b2",
  "status": "queued"
}
```

**Шаг 2 — получение результата:**

``` json
GET /task-result/2d7c72d9-6e28-43d8-88d7-7ca3f151e1b2

{
  "task_id": "2d7c72d9-6e28-43d8-88d7-7ca3f151e1b2",
  "status": "completed",
  "result": {
    "url": "https://www.gutenberg.org/ebooks/84",
    "title": "Frankenstein; or, the modern prometheus",
    "author": "Shelley",
    "gutenberg_id": 84
  }
}
```

---

## Результаты выполнения

### Запуск всех сервисов

``` bash
docker-compose up --build
```

**Результат:**

``` text
✔ Container lab3-db-1              Created
✔ Container lab3-redis-1           Created
✔ Container lab3-parser-1          Created
✔ Container lab3-app-1             Created
✔ Container lab3-celery_worker-1   Created
```

### Проверка через Postman

| Эндпоинт              | Результат                      |
| --------------------- | ------------------------------ |
| GET /                 | 200 OK — сервер работает       |
| POST /parse-url       | 200 OK — данные книги получены |
| POST /parse-url-async | 200 OK — получен task_id       |
| GET /task-result/{id} | 200 OK — результат парсинга    |

### Логи Celery Worker

``` text
[INFO] Task parse_url_task received
[INFO] Task parse_url_task succeeded in 1.28s: {...}
```

---

## Вывод

В ходе выполнения ЛР №3:

| Подзадача | Что сделано                                                                            |
| --------- | -------------------------------------------------------------------------------------- |
| 1         | Упаковала FastAPI приложение, парсер и базу данных в Docker-контейнеры                 |
| 1         | Написала Dockerfile для основного приложения и для парсера                             |
| 1         | Создала docker-compose.yml с 5 сервисами (postgres, redis, parser, app, celery_worker) |
| 2         | Добавила эндпоинт `/parse-url` для синхронного вызова парсера                          |
| 3         | Настроила Celery и Redis для асинхронной обработки                                     |
| 3         | Добавила эндпоинт `/parse-url-async` для отправки задачи в очередь                     |
| 3         | Добавила эндпоинт `/task-result/{task_id}` для получения результата                    |
| 3         | Переиспользовала парсер из лабораторной работы №2                                      |

