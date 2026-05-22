from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, EmailStr, Field


# ========== Auth schemas ==========
class UserRegister(BaseModel):
    login: str = Field(min_length=3, max_length=64)
    email: EmailStr
    password: str = Field(min_length=6)


class UserLogin(BaseModel):
    login: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    login: str
    email: str
    created_at: datetime

    class Config:
        from_attributes = True #позволяет создавать Pydantic модель из SQLAlchemy объекта


class PasswordChange(BaseModel):
    old_password: str
    new_password: str = Field(min_length=6)


# ========== Project schemas ==========
class ProjectCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=128)
    description: Optional[str] = None
    deadline: Optional[datetime] = None


class ProjectResponse(BaseModel):
    id: int
    user_id: int
    name: str
    description: Optional[str]
    deadline: Optional[datetime]
    created_at: datetime

    class Config:
        from_attributes = True


class ProjectDetailResponse(ProjectResponse):
    tasks: List["TaskResponse"] = []


# ========== Category schemas ==========
class CategoryCreate(BaseModel):
    name: str = Field(min_length=1, max_length=64)
    color: str = Field(default="#808080", pattern="^#[0-9a-fA-F]{6}$")  # строка вида #FF4444


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=64)
    color: Optional[str] = Field(None, pattern="^#[0-9a-fA-F]{6}$")


class CategoryResponse(BaseModel):
    id: int
    user_id: int
    name: str
    color: str

    class Config:
        from_attributes = True


# ========== Task schemas ==========
class TaskCreate(BaseModel):
    project_id: Optional[int] = None
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    priority: int = Field(default=1, ge=1, le=5)
    deadline: Optional[datetime] = None
    category_ids: List[int] = []


class TaskUpdate(BaseModel):
    project_id: Optional[int] = None
    title: Optional[str] = Field(None, min_length=1, max_length=255)
    description: Optional[str] = None
    priority: Optional[int] = Field(None, ge=1, le=5)
    status: Optional[str] = None
    deadline: Optional[datetime] = None
    category_ids: Optional[List[int]] = None


class CategoryLinkResponse(BaseModel):
    category_id: int
    category_name: str
    category_color: str
    weight: int
    assigned_at: datetime


class TimeLogResponse(BaseModel):
    id: int
    minutes: int
    description: Optional[str]
    logged_at: datetime

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: int
    user_id: int
    project_id: Optional[int]
    title: str
    description: Optional[str]
    priority: int
    status: str
    deadline: Optional[datetime]
    created_at: datetime
    completed_at: Optional[datetime]
    categories: List[CategoryLinkResponse] = []
    total_time_minutes: int = 0

    class Config:
        from_attributes = True


class TimeLogCreate(BaseModel):
    minutes: int = Field(gt=0, le=1440)  # максимум 24 часа
    description: Optional[str] = Field(None, max_length=255)


# ========== Report schemas ==========
class TaskTimeSummary(BaseModel):
    task_id: int
    task_title: str
    total_minutes: int


class DeadlineAlert(BaseModel):
    task_id: int
    task_title: str
    deadline: datetime
    priority: int
    days_left: int


# Обновление ссылок
ProjectDetailResponse.model_rebuild()
TaskResponse.model_rebuild()