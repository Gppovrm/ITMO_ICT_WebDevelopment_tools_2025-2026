from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os

# Загружаем переменные из .env
load_dotenv()

# Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:postgres@localhost:5432/warriors_db')

# Создаем engine
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Создает все таблицы в базе данных"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Генератор сессий для работы с БД"""
    with Session(engine) as session:
        yield session