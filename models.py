from pydantic import BaseModel
from typing import Optional
from sqlmodel import SQLModel, Field
class Sesion(SQLModel):
    tema:str
    fecha:str
    hora:str
    nombre_mentor:str
    link:str

# Modelo base para distribuidores con mapeo SQL
class Distribuidores(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str = Field(..., min_length=2, max_length=50)
    direccion: str = Field(..., min_length=2, max_length=50)

# Modelo base para componentes con mapeo SQL
class Componente(SQLModel):
    #id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    tipo: str
    marca: str
    modelo: str

# Modelo para incluir ID en las respuestas de componentes
class ComponenteConId(Componente):
    id: int

# Modelo para incluir ID en las respuestas de distribuidores
class DistriConId(Distribuidores):
    id: int

# Modelo para actualizar componentes
class ComponenteActualizado(SQLModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    tipo: Optional[str] = Field(None, min_length=2, max_length=30)
    marca: Optional[str] = Field(None, min_length=2, max_length=30)
    modelo: Optional[str] = Field(None, min_length=2, max_length=30)

# Modelo para actualizar distribuidores
class DistriActualizado(SQLModel):
    nombre: Optional[str] = Field(None, min_length=2, max_length=50)
    direccion: Optional[str] = Field(None, min_length=2, max_length=30)
