from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.schemas.schemas import UserRegister, UserLogin, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_token

# создаём роутер для всех эндпоинтов авторизации
router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserRegister, db: Session = Depends(get_db)):
    # проверяем не занят ли логин
    existing = db.scalar(select(User).where(User.login == user_data.login))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Login already taken")

    # проверяем не занята ли почта
    existing_email = db.scalar(select(User).where(User.email == user_data.email))
    if existing_email:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")

    # создаём нового пользователя пароль сразу хэшируем
    new_user = User(
        login=user_data.login,
        email=user_data.email,
        password_hash=hash_password(user_data.password)
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)  # обновляем объект чтобы получить id из бд
    return UserResponse.model_validate(new_user)


@router.post("/login", response_model=TokenResponse)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    # ищем пользователя по логину
    user = db.scalar(select(User).where(User.login == user_data.login))

    # если пользователь не найден или пароль неверный
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    # создаём jwt токен
    token = create_token(user.id)
    return TokenResponse(access_token=token)