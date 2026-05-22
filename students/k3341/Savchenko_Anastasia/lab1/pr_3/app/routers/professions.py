from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import select
from typing import List
from app.database import get_session
from app.models import Profession, ProfessionDefault

router = APIRouter(prefix='/professions', tags=['Professions'])

@router.get('/', response_model=List[Profession])
def get_professions(session=Depends(get_session)):
    return session.exec(select(Profession)).all()

@router.get('/{profession_id}', response_model=Profession)
def get_profession(profession_id: int, session=Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail='Profession not found')
    return profession

@router.post('/')
def create_profession(profession: ProfessionDefault, session=Depends(get_session)):
    db_profession = Profession.model_validate(profession)
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return {'status': 200, 'data': db_profession}

@router.patch('/{profession_id}')
def update_profession(profession_id: int, profession: ProfessionDefault, session=Depends(get_session)):
    db_profession = session.get(Profession, profession_id)
    if not db_profession:
        raise HTTPException(status_code=404, detail='Profession not found')
    
    profession_data = profession.model_dump(exclude_unset=True)
    for key, value in profession_data.items():
        setattr(db_profession, key, value)
    
    session.add(db_profession)
    session.commit()
    session.refresh(db_profession)
    return db_profession

@router.delete('/{profession_id}')
def delete_profession(profession_id: int, session=Depends(get_session)):
    profession = session.get(Profession, profession_id)
    if not profession:
        raise HTTPException(status_code=404, detail='Profession not found')
    session.delete(profession)
    session.commit()
    return {'status': 200, 'message': 'Deleted'}
