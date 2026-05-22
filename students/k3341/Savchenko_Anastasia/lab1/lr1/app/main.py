from fastapi import FastAPI
from app.routers import auth, users, projects, categories, tasks

# from app.db.database import Base, engine

app = FastAPI(title="TimeManager API", version="1.0.0", description="Task and time management system")

# таблицы теперь создаются через alembic а не автоматически
# Base.metadata.create_all(bind=engine) # рраньше при запуске приложения автоматически создавались таблицы в БД

# FastAPI позволяет разбить код на независимые модули — роутеры. Каждый роутер содержит эндпоинты связанные одной темой
app.include_router(auth.router)  # регистрация и логин
app.include_router(users.router)  # профили пользователей
app.include_router(projects.router)  # управление проектами
app.include_router(categories.router)  # управление категориями
app.include_router(tasks.router)  # задачи время отчёты

#  health check
@app.get("/")
def root():
    return {"message": "Welcome to TimeManager API", "status": "running"}
