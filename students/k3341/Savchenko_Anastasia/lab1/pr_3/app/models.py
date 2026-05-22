from enum import Enum
from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship

class RaceType(str, Enum):
    director = 'director'
    worker = 'worker'
    junior = 'junior'

class SkillWarriorLink(SQLModel, table=True):
    skill_id: Optional[int] = Field(default=None, foreign_key='skill.id', primary_key=True)
    warrior_id: Optional[int] = Field(default=None, foreign_key='warrior.id', primary_key=True)
    level: Optional[int] = None

class Profession(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    description: str = ''
    warriors: List['Warrior'] = Relationship(back_populates='profession')

class Skill(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    description: str = ''
    warriors: List['Warrior'] = Relationship(back_populates='skills', link_model=SkillWarriorLink)

class WarriorDefault(SQLModel):
    race: RaceType
    name: str
    level: int = 1
    profession_id: Optional[int] = Field(default=None, foreign_key='profession.id')

class Warrior(WarriorDefault, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    profession: Optional[Profession] = Relationship(back_populates='warriors')
    skills: List[Skill] = Relationship(back_populates='warriors', link_model=SkillWarriorLink)

class WarriorProfessions(WarriorDefault):
    profession: Optional[Profession] = None
    skills: Optional[List[Skill]] = []

class ProfessionDefault(SQLModel):
    title: str
    description: str = ''

class SkillDefault(SQLModel):
    name: str
    description: str = ''
