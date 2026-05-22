from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from passlib.context import CryptContext
from app.settings import settings

# настраиваем контекст для bcrypt хэширования
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """превращает пароль в необратимый хэш"""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """сравнивает пароль с хэшем при логине"""
    return pwd_context.verify(plain, hashed)


def create_token(user_id: int) -> str:
    """создаёт jwt токен с id пользователя внутри"""
    # токен живёт jwt_expire_minutes минут с момента создания
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_expire_minutes)
    payload = {"sub": str(user_id), "exp": expire}
    # подписываем токен секретным ключом
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_token(token: str) -> Optional[int]:
    """расшифровывает токен и возвращает id пользователя если токен валидный"""
    try:
        data = jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
        user_id = data.get("sub")
        return int(user_id) if user_id else None
    except jwt.InvalidTokenError:
        # при любой ошибке расшифровки (просрочен, подпись не та, битый)
        return None