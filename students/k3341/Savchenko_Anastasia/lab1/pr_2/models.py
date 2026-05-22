from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship


# Перечисление рас
class RaceType(str, Enum):
    director = "director"
    worker = "worker"
    junior = "junior"


# Ассоциативная таблица для связи многие-ко-многим (Warrior <-> Skill)
class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(default=None, foreign_key="skill.id", primary_key=True)
    warrior_id: Optional[int] = Field(default=None, foreign_key="warrior.id", primary_key=True)
    level: Optional[int] = None  # дополнительное поле ассоциации (уровень владения умением)


# Модель профессии (один-ко-многим с воинами)
class Profession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ""

    # Обратная связь: у профессии может быть много воинов
    warriors: List["Warrior"] = Relationship(back_populates="profession")


# Модель умения (многие-ко-многим с воинами)
class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ""

    # Связь многие-ко-многим с воинами через ассоциативную таблицу
    warriors: List["Warrior"] = Relationship(back_populates="skills", link_model=SkillWarriorLink)


# Базовая модель воина (для POST/PATCH запросов, без id и связей)
class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int = 1
    profession_id: Optional[int] = Field(default=None, foreign_key="profession.id")


# Основная модель воина для БД
class Warrior(WarriorDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)

    # Связь с профессией (один-ко-многим)
    profession: Optional[Profession] = Relationship(back_populates="warriors")

    # Связь с умениями (многие-ко-многим)
    skills: List[Skill] = Relationship(back_populates="warriors", link_model=SkillWarriorLink)


# Модель для возврата воина с вложенной профессией
class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None
    skills: Optional[List[Skill]] = []


# Базовая модель профессии (для POST/PATCH)
class ProfessionDefault(SQLModel):
    title: str
    description: str = ""


# Базовая модель умения (для POST/PATCH)
class SkillDefault(SQLModel):
    name: str
    description: str = ""