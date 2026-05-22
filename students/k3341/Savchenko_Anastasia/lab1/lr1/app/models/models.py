from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from app.db.database import Base

# вспом функция для автоматической простановки времени
def now_utc():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    login = Column(String(64), unique=True, nullable=False)      # уникальный логин
    email = Column(String(255), unique=True, nullable=False)    # уникальная почта
    password_hash = Column(String(255), nullable=False)         # храним только хэш а не пароль
    created_at = Column(DateTime(timezone=True), default=now_utc)

    # связи с другими таблицами при удалении пользователя удаляются и его проекты с задачами
    projects = relationship("Project", back_populates="owner", cascade="all, delete-orphan")
    tasks = relationship("Task", back_populates="owner", cascade="all, delete-orphan")


class Project(Base):
    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)

    owner = relationship("User", back_populates="projects")
    tasks = relationship("Task", back_populates="project", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    priority = Column(Integer, default=1)                      # от 1 до 5
    status = Column(String(32), default="pending")            # pending/in_progress/completed/cancelled
    deadline = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=now_utc)
    completed_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="tasks")
    project = relationship("Project", back_populates="tasks")
    time_logs = relationship("TimeLog", back_populates="task", cascade="all, delete-orphan")
    category_links = relationship("TaskCategoryLink", back_populates="task", cascade="all, delete-orphan")


class TimeLog(Base):
    __tablename__ = "time_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), nullable=False)
    minutes = Column(Integer, nullable=False)                 # сколько минут потрачено
    description = Column(String(255), nullable=True)         # комментарий к записи времени
    logged_at = Column(DateTime(timezone=True), default=now_utc)

    task = relationship("Task", back_populates="time_logs")


class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(64), nullable=False)
    color = Column(String(7), default="#808080")              # hex цвет

    task_links = relationship("TaskCategoryLink", back_populates="category", cascade="all, delete-orphan")


class TaskCategoryLink(Base):
    __tablename__ = "task_categories"

    # составной первичный ключ из двух полей
    task_id = Column(Integer, ForeignKey("tasks.id", ondelete="CASCADE"), primary_key=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="CASCADE"), primary_key=True)
    weight = Column(Integer, default=1)                      # дополнительное поле many-to-many
    assigned_at = Column(DateTime(timezone=True), default=now_utc)

    task = relationship("Task", back_populates="category_links")
    category = relationship("Category", back_populates="task_links")

# CASCADE правило бд когда удалишь родителя — удали всё связанное с ним