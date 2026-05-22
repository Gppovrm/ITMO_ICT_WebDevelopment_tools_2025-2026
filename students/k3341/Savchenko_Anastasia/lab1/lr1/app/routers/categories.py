from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import Category
from app.schemas.schemas import CategoryCreate, CategoryUpdate, CategoryResponse
from app.utils.deps import get_current_user

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
def create_category(data: CategoryCreate, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # создаём категорию привязанную к текущему пользователю
    category = Category(
        user_id=current_user.id,
        name=data.name,
        color=data.color
    )
    db.add(category)
    db.commit()
    db.refresh(category)
    return CategoryResponse.model_validate(category)


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # получаем все категории только текущего пользователя
    categories = db.query(Category).filter(Category.user_id == current_user.id).all()
    return [CategoryResponse.model_validate(c) for c in categories]


@router.patch("/{category_id}", response_model=CategoryResponse)
def update_category(
        category_id: int,
        data: CategoryUpdate,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user)
):
    # ищем категорию по id и проверяем что она принадлежит текущему пользователю
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    # обновляем только переданные поля
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(category, key, value)

    db.commit()
    db.refresh(category)
    return CategoryResponse.model_validate(category)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_category(category_id: int, db: Session = Depends(get_db), current_user=Depends(get_current_user)):
    # проверяем что категория существует и принадлежит пользователю
    category = db.query(Category).filter(
        Category.id == category_id,
        Category.user_id == current_user.id
    ).first()
    if not category:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Category not found")

    db.delete(category)
    db.commit()