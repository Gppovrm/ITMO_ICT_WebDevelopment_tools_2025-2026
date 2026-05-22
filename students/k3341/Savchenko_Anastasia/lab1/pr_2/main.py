from fastapi import FastAPI, Depends, HTTPException
from sqlmodel import select
from typing import List
from database import init_db, get_session
from models import (
    Warrior, WarriorDefault, WarriorProfessions,
    Profession, ProfessionDefault,
    Skill, SkillDefault
)

app = FastAPI(title='FastAPI Warriors API with SQLModel')


# Инициализация БД при запуске
@app.on_event("startup")
def on_startup():
    init_db()


# ========== Базовые эндпоинты ==========

@app.get('/')
def root():
    return {'message': 'Hello, Anastasia! Welcome to Warriors API with PostgreSQL!'}


# ========== CRUD для воинов ==========

@app.get('/warriors_list', response_model=List[WarriorProfessions])
def warriors_list(session=Depends(get_session)):
    """Получить всех воинов с вложенными профессиями"""
    return session.exec(select(Warrior)).all()


@app.get('/warrior/{warrior_id}', response_model=WarriorProfessions)
def warrior_get(warrior_id: int, session=Depends(get_session)):
    """Получить воина по ID"""
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    return warrior


@app.post('/warrior')
def warrior_create(warrior: WarriorDefault, session=Depends(get_session)):
    """Создать нового воина"""
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return {"status": 200, "data": db_warrior}


@app.patch('/warrior/{warrior_id}')
def warrior_update(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)):
    """Обновить данные воина (частичное обновление)"""
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
    """Удалить воина"""
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail="Warrior not found")
    session.delete(warrior)
    session.commit()
    return {"status": 200, "message": "Deleted"}


# ========== CRUD для профессий ==========

@app.get('/professions', response_model=List[Profession])
def professions_list(session=Depends(get_session)):
    """Получить все профессии"""
    return session.exec(select(Profession)).all()


@app.get('/profession/{profession_id}', response_model=Profession)
def profession_get(profession_id: int, session=Depends(get_session)):
    """Получить профессию по ID"""
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    return profession


@app.post('/profession')
def profession_create(profession: ProfessionDefault, session=Depends(get_session)):
    """Создать новую профессию"""
    db_profession = Profession.model_validate(profession)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return {"status": 200, "data": db_profession}


@app.patch('/profession/{profession_id}')
def profession_update(profession_id: int, profession: ProfessionDefault, session=Depends(get_session)):
    """Обновить профессию"""
    db_profession = session.get(Profession, profession_id)
    if not db_profession:
        raise HTTPException(status_code=404, detail="Profession not found")

    profession_data = profession.model_dump(exclude_unset=True)
    for key, value in profession_data.items():
        setattr(db_profession, key, value)

    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return db_profession


@app.delete('/profession/{profession_id}')
def profession_delete(profession_id: int, session=Depends(get_session)):
    """Удалить профессию"""
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail="Profession not found")
    session.delete(profession)
    session.commit()
    return {"status": 200, "message": "Deleted"}


# ========== CRUD для умений ==========

@app.get('/skills', response_model=List[Skill])
def skills_list(session=Depends(get_session)):
    """Получить все умения"""
    return session.exec(select(Skill)).all()


@app.get('/skill/{skill_id}', response_model=Skill)
def skill_get(skill_id: int, session=Depends(get_session)):
    """Получить умение по ID"""
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    return skill


@app.post('/skill')
def skill_create(skill: SkillDefault, session=Depends(get_session)):
    """Создать новое умение"""
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return {"status": 200, "data": db_skill}


@app.patch('/skill/{skill_id}')
def skill_update(skill_id: int, skill: SkillDefault, session=Depends(get_session)):
    """Обновить умение"""
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail="Skill not found")

    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(db_skill, key, value)

    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill


@app.delete('/skill/{skill_id}')
def skill_delete(skill_id: int, session=Depends(get_session)):
    """Удалить умение"""
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail="Skill not found")
    session.delete(skill)
    session.commit()
    return {"status": 200, "message": "Deleted"}


# ========== Дополнительные эндпоинты ==========

@app.post('/warrior/{warrior_id}/skill/{skill_id}')
def add_skill_to_warrior(warrior_id: int, skill_id: int, level: int = 1, session=Depends(get_session)):
    """Добавить умение воину (через ассоциативную таблицу)"""
    from models import SkillWarriorLink

    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)

    if not warrior or not skill:
        raise HTTPException(status_code=404, detail="Warrior or Skill not found")

    # Проверяем, есть ли уже связь
    existing = session.exec(
        select(SkillWarriorLink).where(
            SkillWarriorLink.warrior_id == warrior_id,
            SkillWarriorLink.skill_id == skill_id
        )
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="Skill already assigned to warrior")

    link = SkillWarriorLink(warrior_id=warrior_id, skill_id=skill_id, level=level)
    session.add(link)
    session.commit()

    return {"status": 200, "message": f"Skill '{skill.name}' added to warrior '{warrior.name}' with level {level}"}