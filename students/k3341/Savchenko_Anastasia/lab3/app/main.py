from fastapi import FastAPI
from app.routers import auth, users, projects, categories, tasks
from app.db.database import SessionLocal
from app.models.models import Task
from datetime import datetime
from sqlalchemy import select
import httpx
from celery.result import AsyncResult
from celery_app import celery_app

app = FastAPI(title="TimeManager API", version="1.0.0", description="Task and time management system")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(categories.router)
app.include_router(tasks.router)

BOOKS_PROJECT_ID = 1
USER_ID = 1


def save_book_as_task(book_data: dict):
    """Сохраняет распарсенную книгу как задачу в проекте 'Книги к прочтению'"""
    try:
        db = SessionLocal()

        # Проверяем, нет ли уже такой задачи
        existing = db.execute(
            select(Task).where(
                Task.title == f"📖 Прочитать: {book_data['title']}",
                Task.user_id == USER_ID
            )
        ).scalar_one_or_none()

        if existing:
            print(f"[SKIP] Уже есть: {book_data['title']}")
            db.close()
            return False

        # Создаём задачу из книги
        task = Task(
            user_id=USER_ID,
            project_id=BOOKS_PROJECT_ID,
            title=f"📖 Прочитать: {book_data['title']}",
            description=f"Автор: {book_data['author']}\nИсточник: {book_data['url']}\nGutenberg ID: {book_data['gutenberg_id']}",
            priority=3,
            status="pending",
            created_at=datetime.utcnow()
        )

        db.add(task)
        db.commit()
        print(f"[TASK] Создана задача: {book_data['title']}")
        db.close()
        return True

    except Exception as e:
        print(f"[DB ERROR] {e}")
        return False



@app.get("/")
def root():
    return {"message": "Welcome to TimeManager API", "status": "running"}


@app.post("/parse-url")
async def parse_url(url: str):
    """Синхронный парсинг + сохранение в БД"""
    async with httpx.AsyncClient() as client:
        response = await client.post("http://parser:8001/parse", params={"url": url})
        book_data = response.json()

        # Сохраняем как задачу
        if book_data and "error" not in book_data:
            save_book_as_task(book_data)

        return book_data


@app.post("/parse-url-async")
def parse_url_async(url: str):
    """Асинхронный парсинг через Celery"""
    task = celery_app.send_task("parse_url_task", args=[url])
    return {"task_id": task.id, "status": "queued"}


@app.get("/task-result/{task_id}")
def get_task_result(task_id: str):
    """Получить результат асинхронной задачи"""
    task = AsyncResult(task_id, app=celery_app)
    if task.ready():
        result = task.result
        # Если задача выполнена успешно — сохраняем в БД
        if result and "error" not in result:
            save_book_as_task(result)
        return {"task_id": task_id, "status": "completed", "result": result}
    else:
        return {"task_id": task_id, "status": "pending"}