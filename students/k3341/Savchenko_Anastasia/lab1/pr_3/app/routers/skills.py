from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from app.database import get_session
from app.models import Skill, SkillDefault

router = APIRouter(prefix='/skills', tags=['Skills'])

@router.get('/', response_model=List[Skill])
def get_skills(session=Depends(get_session)):
    return session.exec(select(Skill)).all()

@router.get('/{skill_id}', response_model=Skill)
def get_skill(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')
    return skill

@router.post('/')
def create_skill(skill: SkillDefault, session=Depends(get_session)):
    db_skill = Skill.model_validate(skill)
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return {'status': 200, 'data': db_skill}

@router.patch('/{skill_id}')
def update_skill(skill_id: int, skill: SkillDefault, session=Depends(get_session)):
    db_skill = session.get(Skill, skill_id)
    if not db_skill:
        raise HTTPException(status_code=404, detail='Skill not found')
    
    skill_data = skill.model_dump(exclude_unset=True)
    for key, value in skill_data.items():
        setattr(db_skill, key, value)
    
    session.add(db_skill)
    session.commit()
    session.refresh(db_skill)
    return db_skill

@router.delete('/{skill_id}')
def delete_skill(skill_id: int, session=Depends(get_session)):
    skill = session.get(Skill, skill_id)
    if not skill:
        raise HTTPException(status_code=404, detail='Skill not found')
    session.delete(skill)
    session.commit()
    return {'status': 200, 'message': 'Deleted'}
