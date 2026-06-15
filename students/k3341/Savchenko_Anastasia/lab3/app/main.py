from fastapi import FastAPI
from app.routers import auth, users, projects, categories, tasks
import httpx
from celery.result import AsyncResult
from celery_app import celery_app

app = FastAPI(title="TimeManager API", version="1.0.0", description="Task and time management system")

app.include_router(auth.router)
app.include_router(users.router)
app.include_router(projects.router)
app.include_router(categories.router)
app.include_router(tasks.router)

@app.get("/")
def root():
    return {"message": "Welcome to TimeManager API", "status": "running"}


@app.post("/parse-url")
async def parse_url(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.post("http://parser:8001/parse", params={"url": url})
    return response.json()

@app.post("/parse-url-async")
def parse_url_async(url: str):
    task = celery_app.send_task("parse_url_task", args=[url])
    return {"task_id": task.id, "status": "queued"}

@app.get("/task-result/{task_id}")
def get_task_result(task_id: str):
    task = AsyncResult(task_id, app=celery_app)
    if task.ready():
        return {"task_id": task_id, "status": "completed", "result": task.result}
    else:
        return {"task_id": task_id, "status": "pending"}