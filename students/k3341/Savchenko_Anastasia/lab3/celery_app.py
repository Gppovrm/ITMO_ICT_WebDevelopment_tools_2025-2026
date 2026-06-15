from celery import Celery
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent / "parser"))
from parser import parse_gutenberg_book

celery_app = Celery(
    "tasks",
    broker="redis://redis:6379/0",
    backend="redis://redis:6379/0"
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
)

@celery_app.task(name="parse_url_task")
def parse_url_task(url: str):
    return parse_gutenberg_book(url)