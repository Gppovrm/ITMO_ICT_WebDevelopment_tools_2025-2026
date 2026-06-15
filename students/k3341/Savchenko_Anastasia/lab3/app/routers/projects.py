from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from app.db.database import get_db
from app.models.models import Project, Task
from app.schemas.schemas import ProjectCreate, ProjectUpdate, ProjectResponse, ProjectDetailResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/projects", tags=["Projects"])


@router.post("/", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(data: ProjectCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # создаём проект привязанный к текущему пользователю
    project = Project(
        user_id=current_user.id,
        name=data.name,
        description=data.description,
        deadline=data.deadline
    )
    db.add(project)
    db.commit()
    db.refresh(project)  # получаем сгенерированный id
    return ProjectResponse.model_validate(project)


@router.get("/", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # все проекты текущего пользователя
    projects = db.query(Project).filter(Project.user_id == current_user.id).all()
    return [ProjectResponse.model_validate(p) for p in projects]


@router.get("/{project_id}", response_model=ProjectDetailResponse)
def get_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # ищем проект по id и проверяем что он принадлежит пользователю
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # подгружаем задачи этого проекта для вложенного ответа
    tasks = db.query(Task).filter(Task.project_id == project_id).all()
    result = ProjectResponse.model_validate(project).model_dump()
    result["tasks"] = tasks
    return result


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(
        project_id: int,
        data: ProjectUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    # обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(project, key, value)

    db.commit()
    db.refresh(project)
    return ProjectResponse.model_validate(project)


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    project = db.query(Project).filter(
        Project.id == project_id,
        Project.user_id == current_user.id
    ).first()
    if not project:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")

    db.delete(project)  # задачи удалятся сами через cascade
    db.commit()