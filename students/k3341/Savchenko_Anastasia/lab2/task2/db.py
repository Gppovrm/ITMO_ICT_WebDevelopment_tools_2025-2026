import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from datetime import datetime

lr1_path = Path(
    r"C:\Users\Anastasia\PycharmProjects\ITMO_ICT_WebDevelopment_tools_2025-2026\students\k3341\Savchenko_Anastasia\lab1\lr1")
load_dotenv(dotenv_path=lr1_path / ".env")

os.environ["DATABASE_URL"] = os.getenv("DATABASE_URL", "")
os.environ["JWT_SECRET"] = os.getenv("JWT_SECRET", "")
os.environ["JWT_ALGORITHM"] = os.getenv("JWT_ALGORITHM", "")
os.environ["JWT_EXPIRE_MINUTES"] = os.getenv("JWT_EXPIRE_MINUTES", "")

sys.path.insert(0, str(lr1_path))

from app.models.models import Task
from app.db.database import SessionLocal
from sqlalchemy import select

BOOKS_PROJECT_ID = 3
USER_ID = 3


def save_book_as_task(book_data: dict):
    db = None
    try:
        db = SessionLocal()

        existing = db.execute(
            select(Task).where(
                Task.title == f"📖 Прочитать: {book_data['title']}",
                Task.user_id == USER_ID
            )
        ).scalar_one_or_none()

        if existing:
            print(f"[SKIP] Уже есть: {book_data['title']}")
            return False

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
        return True

    except Exception as e:
        print(f"[DB ERROR] {e}")
        return False
    finally:
        if db:
            db.close()


def clear_tasks():
    db = None
    try:
        db = SessionLocal()
        tasks = db.execute(
            select(Task).where(
                Task.project_id == BOOKS_PROJECT_ID,
                Task.user_id == USER_ID
            )
        ).scalars().all()

        for task in tasks:
            db.delete(task)

        db.commit()
        print("[CLEAR] Удалены задачи проекта 'Книги к прочтению'")

    except Exception as e:
        print(f"[CLEAR ERROR] {e}")
    finally:
        if db:
            db.close()
