from typing import Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session
from app.db.database import get_db
from app.models.models import User
from app.utils.security import decode_token

# создаём схему bearer токена без автоматической ошибки, false чтобы самим обрабатывать отсутствие токена
bearer_scheme = HTTPBearer(auto_error=False)

# эта функция будет вызываться перед каждым защищённым эндпоинтом
def get_current_user(
        creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer_scheme),
        db: Session = Depends(get_db)
) -> User:
    # если токен не передан  то сразу отказываем
    if creds is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Not authenticated")

    # расшифровываем токен и получаем id пользователя
    user_id = decode_token(creds.credentials)
    if user_id is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

    # ищем пользователя в базе по id из токена
    user = db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user