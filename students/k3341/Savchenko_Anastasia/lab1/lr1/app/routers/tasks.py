from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session, selectinload
from sqlalchemy import func
from app.db.database import get_db
from app.models.models import Task, TimeLog, TaskCategoryLink, Category
from app.schemas.schemas import (
    TaskCreate, TaskUpdate, TaskResponse, TimeLogCreate,
    TaskTimeSummary, DeadlineAlert
)
from app.utils.deps import get_current_user

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_task_with_relations(db: Session, task_id: int, user_id: int):
    """получает задачу с подгруженными связями (категории)"""
    task = db.query(Task).filter(
        Task.id == task_id,
        Task.user_id == user_id
    ).options(
        selectinload(Task.category_links).selectinload(TaskCategoryLink.category)
    ).first()
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Task not found")
    return task


def calculate_total_time(db: Session, task_id: int) -> int:
    """суммирует все минуты по временным логам задачи"""
    total = db.query(func.sum(TimeLog.minutes)).filter(TimeLog.task_id == task_id).scalar()
    return total or 0  # если нет записей возвращаем 0


def to_task_response(db: Session, task: Task) -> TaskResponse:
    """преобразует объект задачи в pydantic схему с вложенными категориями и временем"""
    categories = [
        {
            "category_id": link.category_id,
            "category_name": link.category.name,
            "category_color": link.category.color,
            "weight": link.weight,
            "assigned_at": link.assigned_at
        }
        for link in task.category_links
    ]
    total_time = calculate_total_time(db, task.id)

    return TaskResponse(
        id=task.id,
        user_id=task.user_id,
        project_id=task.project_id,
        title=task.title,
        description=task.description,
        priority=task.priority,
        status=task.status,
        deadline=task.deadline,
        created_at=task.created_at,
        completed_at=task.completed_at,
        categories=categories,
        total_time_minutes=total_time
    )


@router.post("/", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(data: TaskCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # создаём задачу
    task = Task(
        user_id=current_user.id,
        project_id=data.project_id,
        title=data.title,
        description=data.description,
        priority=data.priority,
        deadline=data.deadline
    )
    db.add(task)
    db.flush()  # отправляем в бд чтобы получить task.id до основного коммита

    # привязываем категории если они указаны
    for cat_id in data.category_ids:
        cat = db.query(Category).filter(
            Category.id == cat_id,
            Category.user_id == current_user.id
        ).first()
        if cat:
            link = TaskCategoryLink(task_id=task.id, category_id=cat_id)
            db.add(link)

    db.commit()
    db.refresh(task)
    return to_task_response(db, task)


@router.get("/", response_model=list[TaskResponse])
def list_tasks(
        status_filter: str = Query(None, description="pending/in_progress/completed/cancelled"),
        project_id: int = Query(None),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    # базовый запрос только задачи текущего пользователя
    query = db.query(Task).filter(Task.user_id == current_user.id)

    # применяем фильтры если они переданы
    if status_filter:
        query = query.filter(Task.status == status_filter)
    if project_id:
        query = query.filter(Task.project_id == project_id)

    # подгружаем категории для каждой задачи
    tasks = query.options(
        selectinload(Task.category_links).selectinload(TaskCategoryLink.category)
    ).all()

    return [to_task_response(db, t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = get_task_with_relations(db, task_id, current_user.id)
    return to_task_response(db, task)


@router.patch("/{task_id}", response_model=TaskResponse)
def update_task(
        task_id: int,
        data: TaskUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    task = get_task_with_relations(db, task_id, current_user.id)

    update_data = data.model_dump(exclude_unset=True)
    category_ids = update_data.pop("category_ids", None)  # отдельно обрабатываем категории

    # обновляем обычные поля
    for key, value in update_data.items():
        setattr(task, key, value)

    # если задача завершена и это первый раз ставим время завершения
    if data.status == "completed" and task.completed_at is None:
        task.completed_at = datetime.now(timezone.utc)

    # обновляем категории если они переданы (заменяем старые новыми)
    if category_ids is not None:
        # удаляем старые связи
        for link in task.category_links:
            db.delete(link)
        # добавляем новые
        for cat_id in category_ids:
            cat = db.query(Category).filter(Category.id == cat_id).first()
            if cat:
                db.add(TaskCategoryLink(task_id=task.id, category_id=cat_id))

    db.commit()
    db.refresh(task)
    return to_task_response(db, task)


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_task(task_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    task = get_task_with_relations(db, task_id, current_user.id)
    db.delete(task)  # time_logs и category_links удалятся через cascade
    db.commit()


@router.post("/{task_id}/time", response_model=TaskResponse)
def add_time_log(
        task_id: int,
        data: TimeLogCreate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    task = get_task_with_relations(db, task_id, current_user.id)

    # добавляем запись о времени
    time_log = TimeLog(
        task_id=task.id,
        minutes=data.minutes,
        description=data.description
    )
    db.add(time_log)
    db.commit()

    return to_task_response(db, task)


@router.get("/report/time-summary", response_model=list[TaskTimeSummary])
def get_time_summary(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    """отчёт сколько времени потрачено на каждую задачу"""
    results = db.query(
        Task.id,
        Task.title,
        func.coalesce(func.sum(TimeLog.minutes), 0).label("total_minutes")  # суммируем минуты null заменяем на 0
    ).outerjoin(TimeLog, TimeLog.task_id == Task.id) \
        .filter(Task.user_id == current_user.id) \
        .group_by(Task.id, Task.title) \
        .all()

    return [TaskTimeSummary(task_id=r[0], task_title=r[1], total_minutes=r[2]) for r in results]


@router.get("/report/upcoming-deadlines", response_model=list[DeadlineAlert])
def get_upcoming_deadlines(
        days: int = Query(default=7, ge=1, le=30),
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    """список задач у которых дедлайн в ближайшие days дней"""
    now = datetime.now(timezone.utc)
    until = now + timedelta(days=days)

    tasks = db.query(Task).filter(
        Task.user_id == current_user.id,
        Task.deadline.isnot(None),  # только задачи с дедлайном
        Task.deadline >= now,       # дедлайн ещё не наступил
        Task.deadline <= until,     # дедлайн в указанном окне
        Task.status != "completed"  # незавершённые
    ).order_by(Task.deadline).all()  # сортируем по приближению дедлайна

    return [
        DeadlineAlert(
            task_id=t.id,
            task_title=t.title,
            deadline=t.deadline,
            priority=t.priority,
            days_left=(t.deadline - now).days  # сколько дней осталось
        )
        for t in tasks
    ]