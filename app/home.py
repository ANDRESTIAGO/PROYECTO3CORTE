from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from models import Componente, ComponenteActualizado, ComponenteConId, DistriActualizado, Distribuidores, DistriConId, Sesion
from typing import Optional
templates = Jinja2Templates(directory="templates")
router = APIRouter()
csv_file = "componentes.csv"

@router.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/info", response_class=HTMLResponse)
async def read_info(request:Request):
    csv_file = "componentes.csv"
    sesiones = pd.read_csv(csv_file)
    sesiones["id"] = sesiones.index
    lista = sesiones.to_dict(orient="records")
    return templates.TemplateResponse("info.html",{"request":request, "sesiones":lista, "titulo":"Datos en tabla"})

@router.get("/comparacion", response_class=HTMLResponse)
async def mostrar_componentes(request: Request):
    csv_file = "componentes.csv"
    sesiones = pd.read_csv(csv_file)
    sesiones["id"] = sesiones.index  # Asignar IDs únicos
    lista = sesiones.to_dict(orient="records")
    return templates.TemplateResponse(
        "comparacion.html",
        {"request": request, "sesiones": lista, "titulo": "Comparación de Componentes"}
    )

# Ruta para procesar la comparación
@router.post("/comparar", response_class=HTMLResponse)
async def comparar_componentes(request: Request, seleccionados: list[int] = Form(...)):
    csv_file = "componentes.csv"
    sesiones = pd.read_csv(csv_file)
    sesiones["id"] = sesiones.index

    # Filtrar los componentes seleccionados
    seleccionados_df = sesiones[sesiones["id"].isin(seleccionados)]
    lista_seleccionados = seleccionados_df.to_dict(orient="records")

    return templates.TemplateResponse(
        "comparacion_seleccionada.html",
        {"request": request, "sesiones": lista_seleccionados, "titulo": "Componentes Seleccionados"}
    )

@router.get("/add", response_class=HTMLResponse)
async def show_form(request:Request):
    return templates.TemplateResponse("add.html", {"request":request})


@router.post("/add")
async def submit_info(
        nombre: str = Form(...),
        tipo:str = Form(...),
        marca:str = Form(...),
        modelo:str = Form(...)
):
    sesion = Componente(nombre=nombre, tipo=tipo, marca=marca, modelo=modelo)
    df = pd.read_csv(csv_file)
    df.loc[len(df)] = [sesion.nombre, sesion.tipo, sesion.marca, sesion.modelo]
    df.to_csv(csv_file, index=True)

    return RedirectResponse(url="/info", status_code=303)


@router.delete("/delete/{id}")
async def eliminar_componente(id: int):
    try:
        df = pd.read_csv(csv_file)
        if id < 0 or id >= len(df):
            raise HTTPException(status_code=404, detail="Componente no encontrado")

        df = df.drop(index=id).reset_index(drop=True)
        df.to_csv(csv_file, index=False)

        return {"message": "Componente eliminado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error eliminando componente: {e}")

@router.put("/update/{id}")
async def actulizar_componente(
        id: int,
        nombre: Optional[str] = Form(None),
        tipo: Optional[str] = Form(None),
        marca: Optional[str] = Form(None),
        modelo: Optional[str] = Form(None)
):
    try:
        df = pd.read_csv(csv_file)
        if id < 0 or id >= len(df):
            raise HTTPException(status_code=404, detail="Componente no encontrado")

        if nombre: df.at[id, "nombre"] = nombre
        if tipo: df.at[id, "tipo"] = tipo
        if marca: df.at[id, "marca"] = marca
        if modelo: df.at[id, "modelo"] = modelo

        df.to_csv(csv_file, index=False)

        return {"message": "Componente actualizado exitosamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error actualizando componente: {e}")
        