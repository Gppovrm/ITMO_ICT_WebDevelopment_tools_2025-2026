from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from app.settings import settings


# базовый класс для всех моделей от него наследуются таблицы
class Base(DeclarativeBase):
    pass


# движок бд отвечает за подключение
engine = create_engine(settings.database_url)

# фабрика сессий создаёт подключения к бд
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


# генератор сессий для fastapi зависимостей
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
# сессия автоматически закрывается после завершения запроса
