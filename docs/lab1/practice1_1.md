# Отчет по практической работе №1.1

**Тема:** Создание базового приложения на FastAPI

## Цель работы

Получить представление о создании серверного приложения с помощью фреймворка FastAPI, освоить базовые CRUD-операции и
использование Pydantic для валидации данных.

## Условия выполнения

Работа выполнялась в рамках лабораторной работы №1 по пути: `students\k3341\Savchenko_Anastasia\lab1\pr_1`

## 1. Установка и запуск

Были установлены необходимые зависимости:

``` bash
pip install fastapi[all]
Запуск сервера осуществлялся командой:
```

``` bash
uvicorn main:app --reload
После запуска автоматическая документация стала доступна по адресу: http://127.0.0.1:8000/docs
```

## 2. Реализация моделей данных

В файле models.py были созданы Pydantic-модели:

``` python
from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class RaceType(Enum):
    director = 'director'
    worker = 'worker'
    junior = 'junior'


class Profession(BaseModel):
    id: int
    title: str
    description: str


class Skill(BaseModel):
    id: int
    name: str
    description: str


class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []
```

Pydantic модели обеспечивают автоматическую валидацию типов данных. Enum RaceType ограничивает возможные значения расы.

## 3. Создание временной базы данных

В файле main.py была создана временная БД:

``` python
temp_bd = [
    Warrior(
        id=1,
        race=RaceType.director,
        name='Alexander',
        level=10,
        profession=Profession(id=1, title='General', description='Commands armies'),
        skills=[
            Skill(id=1, name='Sword', description='Master sword fighter'),
            Skill(id=2, name='Shield', description='Block attacks')
        ]
    ),
    Warrior(
        id=2,
        race=RaceType.worker,
        name='Ivan',
        level=5,
        profession=Profession(id=2, title='Blacksmith', description='Forge weapons'),
        skills=[Skill(id=3, name='Hammer', description='Smash enemies')]
    )
]
```

Временная БД представляет собой список объектов Warrior. Данные хранятся в памяти.

## 4. Реализация CRUD-операций для воинов

``` python
# GET всех воинов
@app.get('/warriors_list')
def warriors_list() -> list[Warrior]:
    return temp_bd


# GET воина по ID
@app.get('/warrior/{warrior_id}')
def warrior_get(warrior_id: int) -> Warrior | dict:
    for warrior in temp_bd:
        if warrior.id == warrior_id:
            return warrior
    return {'error': 'Warrior not found'}


# POST создание воина
@app.post('/warrior')
def warrior_create(warrior: Warrior) -> dict:
    temp_bd.append(warrior)
    return {'status': 200, 'data': warrior.model_dump()}


# PUT обновление воина
@app.put('/warrior/{warrior_id}')
def warrior_update(warrior_id: int, warrior: Warrior) -> dict:
    for i, war in enumerate(temp_bd):
        if war.id == warrior_id:
            temp_bd[i] = warrior
            return {'status': 200, 'data': temp_bd[i].model_dump()}
    return {'error': 'Warrior not found'}


# DELETE удаление воина
@app.delete('/warrior/{warrior_id}')
def warrior_delete(warrior_id: int) -> dict:
    for i, warrior in enumerate(temp_bd):
        if warrior.id == warrior_id:
            temp_bd.pop(i)
            return {'status': 200, 'message': 'Deleted'}
    return {'error': 'Warrior not found'}
```

## 5. Реализация API для профессий

``` python
@app.get('/professions')
def get_professions() -> list[Profession]:
    professions = []
    for warrior in temp_bd:
        if warrior.profession not in professions:
            professions.append(warrior.profession)
    return professions


@app.get('/profession/{profession_id}')
def get_profession(profession_id: int) -> Profession | dict:
    for warrior in temp_bd:
        if warrior.profession.id == profession_id:
            return warrior.profession
    return {'error': 'Profession not found'}
```

## 6. Реализация API для умений

``` python
@app.get('/skills')
def get_skills() -> list[Skill]:
    skills = []
    for warrior in temp_bd:
        for skill in warrior.skills:
            if skill not in skills:
                skills.append(skill)
    return skills


@app.get('/skill/{skill_id}')
def get_skill(skill_id: int) -> Skill | dict:
    for warrior in temp_bd:
        for skill in warrior.skills:
            if skill.id == skill_id:
                return skill
    return {'error': 'Skill not found'}
```

## Результаты выполнения запросов

| Запрос               | Результат                            |
|----------------------|--------------------------------------|
| `GET /warriors_list` | Список из 2 воинов (Alexander, Ivan) |
| `GET /warrior/1`     | Данные воина Alexander               |
| `GET /professions`   | General, Blacksmith                  |
| `GET /skills`        | Sword, Shield, Hammer                |
| `POST /warrior`      | Создание нового воина                |

---

## Использованные возможности FastAPI

- **Pydantic-модели** — валидация данных
- **Аннотация типов** — `list[Warrior]`, `Warrior \| dict`
- **Enum** — ограничение значений расы
- **Автоматическая документация Swagger** — тестирование API

---

## Выводы

В ходе выполнения практической работы были успешно выполнены все задания:

- Создано базовое FastAPI приложение
- Реализована временная БД с данными о воинах
- Выполнен полный CRUD-интерфейс (`GET`, `POST`, `PUT`, `DELETE`)
- Созданы Pydantic-модели для валидации данных
- Реализованы API для связанных объектов (профессии и умения)

### Полученные навыки

- Создание REST API на FastAPI
- Валидация данных с Pydantic
- Работа с вложенными объектами
- Использование автоматической документации Swagger  