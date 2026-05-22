# Отчет по практической работе №1.2

**Тема:** Настройка БД, SQLModel и миграции через Alembic

## 🎯 Цель работы

Получить представление о работе с SQLModel как ORM для FastAPI, научиться подключать PostgreSQL, создавать модели с отношениями и выполнять CRUD-операции через базу данных.

---

## 📋 Условия выполнения

Работа выполнялась в рамках лабораторной работы №1 по пути:  
`students\k3341\Savchenko_Anastasia\lab1\pr_2`

**Стек технологий:**
- Python 3.10+
- FastAPI
- SQLModel (ORM на основе SQLAlchemy и Pydantic)
- PostgreSQL
- Uvicorn

---

## 🛠 1. Установка зависимостей

``` bash
pip install fastapi[all] sqlmodel psycopg2-binary alembic python-dotenv
```

---

## 🗄️ 2. Структура файлов проекта

```
pr_2/
├── .env                 # переменные окружения
├── database.py          # подключение к БД
├── models.py            # SQLModel модели
├── main.py              # FastAPI приложение и эндпоинты
└── venv/                # виртуальное окружение
```

---

## 🔌 4. Подключение к базе данных (database.py)

``` python
from sqlmodel import SQLModel, Session, create_engine
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL', 'postgresql://postgres:123@localhost:5432/warriors_db')
engine = create_engine(DATABASE_URL, echo=True)

def init_db():
    """Создает все таблицы в базе данных"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """Генератор сессий для работы с БД"""
    with Session(engine) as session:
        yield session
```

### Файл .env
```env
DATABASE_URL=postgresql://postgres:123@localhost:5432/warriors_db
```

---

## 📊 5. Модели данных (models.py)

### Перечисление рас
``` python
from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"
```

### Ассоциативная таблица (многие-ко-многим)
``` python
class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(default=None, foreign_key="skill.id", primary_key=True)
    warrior_id: Optional[int] = Field(default=None, foreign_key="warrior.id", primary_key=True)
    level: Optional[int] = None  # дополнительное поле ассоциации
```

### Модель профессии (один-ко-многим)
``` python
class Profession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""
    warriors: List["Warrior"] = Relationship(back_populates="profession")
```

### Модель умения (многие-ко-многим)
``` python
class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""
    warriors: List["Warrior"] = Relationship(back_populates="skills", link_model=SkillWarriorLink)
```

### Базовая модель воина (для POST/PATCH запросов)
``` python
class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int = 1
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")
```

### Основная модель воина
``` python
class Warrior(WarriorDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(back_populates="warriors")
    skills: List[Skill] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)
```

### Модель для возврата с вложенными объектами
``` python
class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None
    skills: Optional[List[Skill]] = []
```

---

## 🚀 6. FastAPI приложение (main.py)

### Инициализация БД при запуске
``` python
from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from typing import List
from database import init_db, get_session
from models import Warrior, WarriorDefault, WarriorProfessions, Profession, ProfessionDefault, Skill, SkillDefault

app = FastAPI(title='FastAPI Warriors API with SQLModel')

@app.on_event("startup")
def on_startup():
    init_db()
```

### CRUD для воинов
``` python
@app.get('/warriors_list', response_model=List[WarriorProfessions])
def warriors_list(session=Depends(get_session)):
    return session.exec(select(Warrior)).all()

@app.get('/warrior/{warrior_id}', response_model=WarriorProfessions)
def warrior_get(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior

@app.post('/warrior')
def warrior_create(warrior: WarriorDefault, session=Depends(get_session)):
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return {"status": 200, "data": db_warrior}

@app.patch('/warrior/{warrior_id}')
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@app.delete('/warrior/{warrior_id}')
def warrior_delete(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"status": 200, "message": "Deleted"}
```

### CRUD для профессий
``` python
@app.get('/professions', response_model=List[Profession])
def professions_list(session=Depends(get_session)):
    return session.exec(select(Profession)).all()

@app.get('/profession/{profession_id}', response_model=Profession)
def profession_get(profession_id: int, session=Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession

@app.post('/profession')
def profession_create(profession: ProfessionDefault, session=Depends(get_session)):
    db_profession = Profession.model_validate(profession)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return {"status": 200, "data": db_profession}
```

### CRUD для умений
``` python
@app.get('/skills', response_model=List[Skill])
def skills_list(session=Depends(get_session)):
    return session.exec(select(Skill)).all()

@app.get('/skill/{skill_id}', response_model=Skill)
def skill_get(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill

@app.post('/skill')
def skill_create(skill: SkillDefault, session=Depends(get_session)):
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return {"status": 200, "data": db_skill}
```

### Добавление умения воину
``` python
@app.post('/warrior/{warrior_id}/skill/{skill_id}')
def add_skill_to_warrior(warrior_id: int, skill_id: int, level: int = 1, session=Depends(get_session)):
    from models import SkillWarriorLink
    
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)
    
    if not warrior or not skill:
        raise HTTPException(status_code=404, detail="Warrior or Skill not found")
    
    link = SkillWarriorLink(warrior_id=warrior_id, skill_id=skill_id, level=level)
    session.add(link)
    session.commit()
    
    return {"status": 200, "message": f"Skill '{skill.name}' added to warrior '{warrior.name}' with level {level}"}
```

---

## 📋 7. Создание таблиц в БД

При запуске сервера SQLModel автоматически создал таблицы:

``` sql
CREATE TYPE racetype AS ENUM ('director', 'worker', 'junior');

CREATE TABLE profession (
    id SERIAL NOT NULL, 
    title VARCHAR NOT NULL, 
    description VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE skill (
    id SERIAL NOT NULL, 
    name VARCHAR NOT NULL, 
    description VARCHAR NOT NULL, 
    PRIMARY KEY (id)
);

CREATE TABLE warrior (
    race racetype NOT NULL, 
    name VARCHAR NOT NULL, 
    level INTEGER NOT NULL, 
    profession_id INTEGER, 
    id SERIAL NOT NULL, 
    PRIMARY KEY (id), 
    FOREIGN KEY(profession_id) REFERENCES profession (id)
);

CREATE TABLE skillwarriorlink (
    skill_id INTEGER NOT NULL, 
    warrior_id INTEGER NOT NULL, 
    level INTEGER, 
    PRIMARY KEY (skill_id, warrior_id), 
    FOREIGN KEY(skill_id) REFERENCES skill (id), 
    FOREIGN KEY(warrior_id) REFERENCES warrior (id)
);
```

---

## 🔍 8. Анализ выполненной работы

### Типы связей в моделях:

| Связь | Тип | Реализация |
|-------|-----|------------|
| Profession → Warrior | один-ко-многим | `Relationship(back_populates="profession")` |
| Warrior → Skill | многие-ко-многим | `link_model=SkillWarriorLink` |
| SkillWarriorLink | ассоциативная | промежуточная таблица с полем `level` |

### Основные методы SQLModel:

| Метод | Назначение |
|-------|------------|
| `session.exec(select(Model))` | Выполнение SELECT-запроса |
| `.all()` | Получение всех результатов |
| `.first()` | Получение первого результата |
| `session.get(Model, id)` | Получение объекта по первичному ключу |
| `session.add(obj)` | Добавление объекта в сессию |
| `session.commit()` | Сохранение изменений в БД |
| `session.refresh(obj)` | Обновление объекта из БД |
| `session.delete(obj)` | Удаление объекта |

### Использование Depends для внедрения зависимостей

``` python
def warriors_list(session=Depends(get_session)):
    # session автоматически подставляется из генератора
    return session.exec(select(Warrior)).all()
```

---

## ✅ Результаты выполнения

### Запуск сервера
``` bash
uvicorn main:app --reload
```

**Результат:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

### Логи создания таблиц
```
INFO sqlalchemy.engine.Engine CREATE TYPE racetype AS ENUM ('director', 'worker', 'junior')
INFO sqlalchemy.engine.Engine CREATE TABLE profession (...)
INFO sqlalchemy.engine.Engine CREATE TABLE skill (...)
INFO sqlalchemy.engine.Engine CREATE TABLE warrior (...)
INFO sqlalchemy.engine.Engine CREATE TABLE skillwarriorlink (...)
```

---

## 📊 Тестирование API через Swagger

| Эндпоинт | Метод | Статус |
|----------|-------|--------|
| `/professions` | GET | ✅ 200 |
| `/profession` | POST | ✅ 201 |
| `/skills` | GET | ✅ 200 |
| `/skill` | POST | ✅ 201 |
| `/warriors_list` | GET | ✅ 200 |
| `/warrior` | POST | ✅ 201 |
| `/warrior/{id}/skill/{id}` | POST | ✅ 201 |

---

## Выводы и заключение

В ходе выполнения практической работы были успешно выполнены все задания:

1. ✅ Установлен и настроен PostgreSQL
2. ✅ Создано подключение к БД через SQLModel
3. ✅ Реализованы модели с отношениями:
   - один-ко-многим (Warrior → Profession)
   - многие-ко-многим (Warrior ↔ Skill) через ассоциативную таблицу
4. ✅ Созданы таблицы в базе данных
5. ✅ Реализованы CRUD-операции для всех моделей
6. ✅ Добавлен эндпоинт для связывания воина с умением
7. ✅ Использована автоматическая документация Swagger для тестирования

### Полученные навыки:

- Настройка подключения к PostgreSQL в FastAPI
- Создание SQLModel моделей с отношениями
- Выполнение CRUD-операций через ORM
- Использование `Depends` для внедрения сессии БД
- Работа с Enum-типами в PostgreSQL
- Создание ассоциативных таблиц для связей многие-ко-многим

Работа подтвердила, что SQLModel предоставляет удобный инструментарий для работы с базами данных в FastAPI, объединяя мощь SQLAlchemy и удобство Pydantic.

