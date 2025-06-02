from fastapi import APIRouter, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from models import Componente, ComponenteActualizado, ComponenteConId, DistriActualizado, Distribuidores, DistriConId, Sesion

templates = Jinja2Templates(directory="templates")
router = APIRouter()
csv_file = "capacitaciones_mintic.csv"

@router.get("/home", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})


@router.get("/info", response_class=HTMLResponse)
async def read_info(request:Request):
    csv_file = "capacitaciones_mintic.csv"
    sesiones = pd.read_csv(csv_file)
    sesiones["id"] = sesiones.index
    lista = sesiones.to_dict(orient="records")
    return templates.TemplateResponse("comparacion.html",{"request":request, "sesiones":lista, "titulo":"Datos en tabla"})

@router.get("/comparacion", response_class=HTMLResponse)
async def comparacion_componentes(request: Request):
    # Archivo CSV con los datos de los componentes
    csv_file = "componentes.csv"
    
    # Leer datos del archivo CSV
    try:
        componentes = pd.read_csv(csv_file)
    except FileNotFoundError:
        return templates.TemplateResponse(
            "error.html",
            {"request": request, "error": "El archivo de datos no se encontró.", "titulo": "Error"}
        )

    # Agregar un ID para facilitar la manipulación
    componentes["id"] = componentes.index

    # Filtrar solo los dos componentes seleccionados (puedes ajustar este filtro)
    seleccionados = componentes.head(2)  # Aquí seleccionamos los dos primeros componentes como ejemplo
    
    # Convertir a una lista de diccionarios
    lista_componentes = seleccionados.to_dict(orient="records")

    # Renderizar la plantilla con los datos
    return templates.TemplateResponse(
        "comparacion.html",
        {"request": request, "sesiones": lista_componentes, "titulo": "Comparación de Componentes"}
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


@router.get("/detail/{id}", response_class=HTMLResponse)
def detalle_sesion(request: Request, id: int):
    df = pd.read_csv(csv_file)

    if id < 0 or id >= len(df):
        html_content = """
                <html>
                    <head>
                        <title>ANDRESTIAGO</title>
                    </head>
                    <body>
                        <h1>Look ma! HTML!</h1>
                    </body>
                </html>
                """
        return HTMLResponse(content=html_content, status_code=404)

    fila = df.iloc[id]

    sesion = {
        "tema": fila["Tema"],
        "fecha": fila["Fecha"],
        "hora": fila["Hora"],
        "nombre_mentor": fila["Mentor"],
        "link": fila["Enlace"]
    }

    return templates.TemplateResponse("detail.html", {"request": request, "sesion": sesion})



@router.get("/html", response_class=HTMLResponse)
async def pure_html():
    html_content = """
        <html>
            <head>
                <title>ANDRESTIAGO</title>
            </head>
            <body>
                <h1>Look ma! HTML!</h1>
            </body>
        </html>
        """
    return HTMLResponse(content=html_content, status_code=200)