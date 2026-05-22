from fastapi import FastAPI
from models import Warrior, Profession, Skill, RaceType

app = FastAPI(title='FastAPI Warriors API')

# Временная БД с использованием Pydantic моделей (Хранит данные в памяти, пока сервер запущен. При остановке сервера данные теряются.)
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


@app.get('/')
def root():
    return {'message': 'Hello, Anastasia!'}


@app.get('/hello/{name}')
def say_hello(name: str):
    return {'message': f'Hello {name}!'}


@app.get('/warriors_list')
def warriors_list() -> list[Warrior]:
    return temp_bd


@app.get('/warrior/{warrior_id}')
def warrior_get(warrior_id: int) -> Warrior | dict:
    for warrior in temp_bd:
        if warrior.id == warrior_id:
            return warrior
    return {'error': 'Warrior not found'}


@app.post('/warrior')
def warrior_create(warrior: Warrior) -> dict:
    temp_bd.append(warrior)
    return {'status': 200, 'data': warrior.model_dump()}


@app.put('/warrior/{warrior_id}')
def warrior_update(warrior_id: int, warrior: Warrior) -> dict:
    for i, war in enumerate(temp_bd):
        if war.id == warrior_id:
            temp_bd[i] = warrior
            return {'status': 200, 'data': temp_bd[i].model_dump()}
    return {'error': 'Warrior not found'}


@app.delete('/warrior/{warrior_id}')
def warrior_delete(warrior_id: int) -> dict:
    for i, warrior in enumerate(temp_bd):
        if warrior.id == warrior_id:
            temp_bd.pop(i)
            return {'status': 200, 'message': 'Deleted'}
    return {'error': 'Warrior not found'}


# ========== API для профессий ==========

@app.get('/professions')
def get_professions() -> list[Profession]:
    """Получить все профессии"""
    professions = []
    for warrior in temp_bd:
        if warrior.profession not in professions:
            professions.append(warrior.profession)
    return professions


@app.get('/profession/{profession_id}')
def get_profession(profession_id: int) -> Profession | dict:
    """Получить профессию по id"""
    for warrior in temp_bd:
        if warrior.profession.id == profession_id:
            return warrior.profession
    return {'error': 'Profession not found'}


@app.post('/profession')
def create_profession(profession: Profession) -> dict:
    """Создать новую профессию"""
    # Просто возвращаем созданную профессию
    return {'status': 200, 'data': profession.model_dump()}


# ========== API для умений ==========

@app.get('/skills')
def get_skills() -> list[Skill]:
    """Получить все умения"""
    skills = []
    for warrior in temp_bd:
        for skill in warrior.skills:
            if skill not in skills:
                skills.append(skill)
    return skills


@app.get('/skill/{skill_id}')
def get_skill(skill_id: int) -> Skill | dict:
    """Получить умение по id"""
    for warrior in temp_bd:
        for skill in warrior.skills:
            if skill.id == skill_id:
                return skill
    return {'error': 'Skill not found'}
