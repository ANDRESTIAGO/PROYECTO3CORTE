from fastapi import APIRouter, Request, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
import pandas as pd
from models import Componente, ComponenteActualizado, ComponenteConId, DistriActualizado, Distribuidores, DistriConId, Sesion, Orden
from typing import Optional
templates = Jinja2Templates(directory="templates")
router = APIRouter()
csv_file = "componentes.csv"
prueba_file = "pruebas.csv"

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

#---------------------------------------------------------------------------------------------------------------------------------------------------
@router.get("/motherboard", response_class=HTMLResponse)
async def get_motherboards(request: Request):
    csv_file = "componentes.csv"
    df = pd.read_csv(csv_file)
    motherboards = df[df["tipo"] == "Motherboard"].to_dict(orient="records")
    return templates.TemplateResponse(
        "motherboard.html", {"request": request, "motherboards": motherboards}
    )

@router.get("/compatiblesi", response_class=HTMLResponse)
async def get_compatible_components(request: Request, socket: str, tipo_ram: Optional[str] = None):
    csv_file = "componentes.csv"
    df = pd.read_csv(csv_file)

    cpus = df[(df["tipo"] == "CPU") & (df["socket"] == socket)].to_dict(orient="records")
    ram = []
    if tipo_ram:
        ram = df[(df["tipo"] == "RAM") & (df["tipo_ram"] == tipo_ram)].to_dict(orient="records")
    gpus = df[df["tipo"] == "GPU"].to_dict(orient="records")
    fuentes = df[df["tipo"] == "Power Supply"].to_dict(orient="records")

    return templates.TemplateResponse(
        "compatibles.html",
        {"request": request, "cpus": cpus, "ram": ram, "gpus": gpus, "fuentes": fuentes}
    )


@router.post("/orden/actualizar", response_class=HTMLResponse)
async def actualizar_componente(id: int = Form(...), nuevo_id: int = Form(...)):
    componentes_file = "componentes.csv"
    orden_file = "orden.csv"

    # Leer componentes disponibles y la orden
    componentes = pd.read_csv(componentes_file)

    try:
        orden = pd.read_csv(orden_file)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No hay orden para actualizar")

    # Verificar si el nuevo componente existe
    nuevo_componente = componentes[componentes["id"] == nuevo_id]
    if nuevo_componente.empty:
        raise HTTPException(status_code=404, detail="Componente no encontrado")

    # Reemplazar componente
    orden.loc[orden["id"] == id, :] = nuevo_componente.iloc[0]
    orden.to_csv(orden_file, index=False)

    return RedirectResponse(url="/orden", status_code=303)


@router.post("/orden/eliminar", response_class=HTMLResponse)
async def eliminar_componente(id: int = Form(...)):
    orden_file = "orden.csv"

    try:
        orden = pd.read_csv(orden_file)
        orden = orden[orden["id"] != id]
        orden.to_csv(orden_file, index=False)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No hay orden para modificar")

    return RedirectResponse(url="/orden", status_code=303)

@router.post("/orden/agregar", response_class=HTMLResponse)
async def agregar_componente(id: int = Form(...)):
    componentes_file = "componentes.csv"
    orden_file = "orden.csv"

    # Leer componentes disponibles
    componentes = pd.read_csv(componentes_file)

    # Verificar si el componente existe
    componente = componentes[componentes["id"] == id]
    if componente.empty:
        raise HTTPException(status_code=404, detail="Componente no encontrado")

    # Leer o crear archivo de orden
    try:
        orden = pd.read_csv(orden_file)
    except FileNotFoundError:
        orden = pd.DataFrame(columns=componentes.columns)

    # Evitar duplicados
    if id in orden["id"].values:
        raise HTTPException(status_code=400, detail="El componente ya está en la orden")

    # Agregar el componente a la orden
    orden = pd.concat([orden, componente], ignore_index=True)
    orden.to_csv(orden_file, index=False)

    return RedirectResponse(url="/orden", status_code=303)


@router.get("/orden", response_class=HTMLResponse)
async def ver_orden(request: Request):
    orden_file = "orden.csv"

    try:
        orden = pd.read_csv(orden_file)
    except FileNotFoundError:
        orden = pd.DataFrame()

    # Asegurarte de que el DataFrame no esté vacío
    if orden.empty:
        componentes = []
    else:
        componentes = orden.to_dict(orient="records")

    return templates.TemplateResponse(
        "orden.html", {"request": request, "componentes": componentes}
    )
#-----------------------------------------------------------------------------------------------------
@router.get("/add", response_class=HTMLResponse)
async def show_form(request: Request):
    df = pd.read_csv("componentes.csv")

    motherboards = df[df["tipo"] == "Motherboard"].to_dict(orient="records")
    cpus = df[df["tipo"] == "CPU"].to_dict(orient="records")
    rams = df[df["tipo"] == "RAM"].to_dict(orient="records")
    gpus = df[df["tipo"] == "GPU"].to_dict(orient="records")
    discos = df[df["tipo"].isin(["HDD", "SSD"])].to_dict(orient="records")

    return templates.TemplateResponse("add.html", {
        "request": request,
        "motherboards": motherboards,
        "cpus": cpus,
        "rams": rams,
        "gpus": gpus,
        "discos": discos
    })



@router.post("/add")
async def submit_info(
    nombre_orden: str = Form(...),
    motherboard_id: int = Form(...),
    cpu_id: int = Form(...),
    ram_id: int = Form(...),
    gpu_id: int = Form(...),
    disco_id: int = Form(...)
):
    df = pd.read_csv("componentes.csv")
    orden_file = "orden.csv"

    # Obtener componentes
    mb = df[df["id"] == motherboard_id].iloc[0]
    cpu = df[df["id"] == cpu_id].iloc[0]
    ram = df[df["id"] == ram_id].iloc[0]
    gpu = df[df["id"] == gpu_id].iloc[0]
    disco = df[df["id"] == disco_id].iloc[0]

    # Validaciones de compatibilidad
    if cpu["socket"] != mb["socket"]:
        raise HTTPException(status_code=400, detail="El CPU no es compatible con el socket de la motherboard.")

    if "tipo_ram" in mb and "tipo_ram" in ram and ram["tipo_ram"] != mb["tipo_ram"]:
        raise HTTPException(status_code=400, detail="La RAM no es compatible con la motherboard.")

    try:
        orden = pd.read_csv(orden_file)
    except FileNotFoundError:
        orden = pd.DataFrame(columns=["orden", "id", "nombre", "tipo", "marca", "modelo"])

    seleccionados = pd.DataFrame([
        {"orden": nombre_orden, **mb.to_dict()},
        {"orden": nombre_orden, **cpu.to_dict()},
        {"orden": nombre_orden, **ram.to_dict()},
        {"orden": nombre_orden, **gpu.to_dict()},
        {"orden": nombre_orden, **disco.to_dict()}
    ])

    orden = pd.concat([orden, seleccionados], ignore_index=True)
    orden.to_csv(orden_file, index=False)

    return RedirectResponse(url="/orden", status_code=303)

@router.get("/modificar", response_class=HTMLResponse)
async def modificar_orden(request: Request):
    try:
        df_orden = pd.read_csv("orden.csv")
        df_componentes = pd.read_csv("componentes.csv")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No se encontraron archivos de orden o componentes")

    ordenes = df_orden["orden"].unique().tolist()
    componentes_por_orden = {
        nombre: df_orden[df_orden["orden"] == nombre].to_dict(orient="records")
        for nombre in ordenes
    }

    return templates.TemplateResponse("modificar_orden.html", {
        "request": request,
        "ordenes": ordenes,
        "componentes_por_orden": componentes_por_orden,
        "todos_componentes": df_componentes.to_dict(orient="records")
    })

@router.post("/modificar", response_class=HTMLResponse)
async def aplicar_modificacion(
    orden: str = Form(...),
    componente_id_original: int = Form(...),
    nuevo_id: int = Form(...)
):
    df_orden = pd.read_csv("orden.csv")
    df_componentes = pd.read_csv("componentes.csv")

    nuevo = df_componentes[df_componentes["id"] == nuevo_id]
    if nuevo.empty:
        raise HTTPException(status_code=404, detail="Nuevo componente no encontrado")

    index = df_orden[(df_orden["orden"] == orden) & (df_orden["id"] == componente_id_original)].index
    if index.empty:
        raise HTTPException(status_code=404, detail="Componente original no encontrado en la orden")

    for col in nuevo.columns:
        df_orden.loc[index, col] = nuevo.iloc[0][col]

    df_orden.to_csv("orden.csv", index=False)
    return RedirectResponse(url="/ordenes", status_code=303)




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
    
@router.get("/menu", response_class=HTMLResponse)
async def read_home(request: Request):
    return templates.TemplateResponse("menu.html", {"request": request})

@router.get("/ordenes", response_class=HTMLResponse)
async def ver_ordenes(request: Request):
    orden_file = "orden.csv"

    try:
        df = pd.read_csv(orden_file)
    except FileNotFoundError:
        df = pd.DataFrame(columns=["orden", "id", "nombre", "tipo", "marca", "modelo"])

    # Agrupar por nombre de orden
    ordenes_agrupadas = {}
    for _, row in df.iterrows():
        nombre_orden = row["orden"]
        if nombre_orden not in ordenes_agrupadas:
            ordenes_agrupadas[nombre_orden] = []
        ordenes_agrupadas[nombre_orden].append(row.to_dict())

    return templates.TemplateResponse(
        "orden.html",
        {"request": request, "ordenes": ordenes_agrupadas}
    )

@router.get("/eliminar", response_class=HTMLResponse)
async def mostrar_ordenes_para_eliminar(request: Request):
    try:
        df = pd.read_csv("orden.csv")
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No hay órdenes registradas")

    nombres_ordenes = df["orden"].unique().tolist()

    return templates.TemplateResponse("eliminar.html", {
        "request": request,
        "ordenes": nombres_ordenes
    })


@router.post("/eliminar", response_class=HTMLResponse)
async def eliminar_orden_completa(orden: str = Form(...)):
    try:
        df = pd.read_csv("orden.csv")
        df = df[df["orden"] != orden]
        df.to_csv("orden.csv", index=False)
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="No hay órdenes para eliminar")

    return RedirectResponse(url="/ordenes", status_code=303)
