from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from app.database import get_session
from app.models import Warrior, WarriorDefault, WarriorProfessions, Skill

router = APIRouter(prefix='/warriors', tags=['Warriors'])

@router.get('/', response_model=List[WarriorProfessions])
def get_warriors(session=Depends(get_session)):
    warriors = session.exec(select(Warrior)).all()
    return warriors

@router.get('/{warrior_id}', response_model=WarriorProfessions)
def get_warrior(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail='Warrior not found')
    return warrior

@router.post('/')
def create_warrior(warrior: WarriorDefault, session=Depends(get_session)):
    db_warrior = Warrior.model_validate(warrior)
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return {'status': 200, 'data': db_warrior}

@router.patch('/{warrior_id}')
def update_warrior(warrior_id: int, warrior: WarriorDefault, session=Depends(get_session)):
    db_warrior = session.get(Warrior, warrior_id)
    if not db_warrior:
        raise HTTPException(status_code=404, detail='Warrior not found')
    
    warrior_data = warrior.model_dump(exclude_unset=True)
    for key, value in warrior_data.items():
        setattr(db_warrior, key, value)
    
    session.add(db_warrior)
    session.commit()
    session.refresh(db_warrior)
    return db_warrior

@router.delete('/{warrior_id}')
def delete_warrior(warrior_id: int, session=Depends(get_session)):
    warrior = session.get(Warrior, warrior_id)
    if not warrior:
        raise HTTPException(status_code=404, detail='Warrior not found')
    session.delete(warrior)
    session.commit()
    return {'status': 200, 'message': 'Deleted'}

@router.post('/{warrior_id}/skill/{skill_id}')
def add_skill_to_warrior(warrior_id: int, skill_id: int, level: int = 1, session=Depends(get_session)):
    from app.models import SkillWarriorLink
    
    warrior = session.get(Warrior, warrior_id)
    skill = session.get(Skill, skill_id)
    
    if not warrior or not skill:
        raise HTTPException(status_code=404, detail='Warrior or Skill not found')
    
    link = SkillWarriorLink(warrior_id=warrior_id, skill_id=skill_id, level=level)
    session.add(link)
    session.commit()
    
    return {'status': 200, 'message': 'Skill added to warrior'}
