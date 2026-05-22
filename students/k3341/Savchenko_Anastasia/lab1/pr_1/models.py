from enum import Enum
from typing import Optional, List
from pydantic import BaseModel


class RaceType(Enum):
    director = 'director'
    worker = 'worker'
    junior = 'junior'


# Модель профессии (id, title, description)
class Profession(BaseModel):
    id: int
    title: str
    description: str


# Модель умения (id, name, description)
class Skill(BaseModel):
    id: int
    name: str
    description: str


# Модель воина (id, race, name, level, profession, skills)
class Warrior(BaseModel):
    id: int
    race: RaceType
    name: str
    level: int
    profession: Profession
    skills: Optional[List[Skill]] = []
