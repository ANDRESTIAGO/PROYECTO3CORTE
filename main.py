from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request

from . import home
from .models import ComponenteActualizado, Componente, ComponenteConId, DistriConId, DistriActualizado, Distribuidores

from sqlalchemy import select
#from .db import get_session, init_db
from sqlalchemy.ext.asyncio import AsyncSession

app = FastAPI()


app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

app.include_router(home.router)

templates = Jinja2Templates(directory="templates")


'''@app.lifespan
async def app_lifespan(app):
    await init_db()
    yield'''
    
# Endpoints de Componentes
'''@app.get("/componentes", response_model=List[ComponenteConId])
async def obtener_componentes(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Componente))
    componentes = result.scalars().all()
    return [ComponenteConId.from_orm(comp) for comp in componentes]'''

