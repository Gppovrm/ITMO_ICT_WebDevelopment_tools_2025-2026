from fastapi import FastAPI
from app.database import init_db
from app.routers import warriors, professions, skills

app = FastAPI(title='FastAPI Warriors API', version='1.0.0')

@app.on_event('startup')
def on_startup():
    init_db()

@app.get('/')
def root():
    return {'message': 'Welcome to Warriors API!'}

app.include_router(warriors.router)
app.include_router(professions.router)
app.include_router(skills.router)
