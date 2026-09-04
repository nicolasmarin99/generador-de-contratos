"""Capa web: FastAPI.

Fijate en lo que este archivo NO hace: no sabe redactar contratos, no sabe
validar un RUT, no sabe donde viven las plantillas .docx. Solo traduce
peticiones HTTP a llamadas al dominio (modelos.py + motor.py) y devuelve HTML.

Ese es el trabajo de una capa de interfaz. Si un dia quieres una app de
escritorio, escribes otra capa como esta y el resto del proyecto no se entera.

EL FLUJO
--------
    GET  /                    elegir que tipo de contrato generar
    GET  /nuevo/{tipo}        formulario con los datos del cliente
    POST /generar             construye el contrato, renderiza la plantilla
                               exacta, la registra en el historial y ofrece
                               la descarga
    GET  /historial            contratos generados en este equipo, con busqueda
    GET  /descargar/{nombre}  entrega el .docx generado

No hay paso de "subir un documento": la plantilla siempre es la oficial de
plantillas/, nunca una que suba el usuario. Eso es lo que garantiza que el
texto legal generado sea identico al de la plantilla, letra por letra.
"""

from datetime import date
from pathlib import Path

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import ValidationError

from contratos import historial
from contratos.modelos import Cliente, ContratoImpactOnline, ContratoTechTool
from contratos.motor import PlantillaIncompleta, generar_docx
from contratos.rutas import raiz_app

RAIZ = raiz_app()
DIR_SALIDA = RAIZ / "salida"
DIR_HISTORIAL = RAIZ / "historial"

DIR_SALIDA.mkdir(exist_ok=True)

app = FastAPI(title="Generador de contratos")
app.mount("/static", StaticFiles(directory=RAIZ / "web" / "static"), name="static")
plantillas_html = Jinja2Templates(directory=RAIZ / "web" / "templates")

#: Los 4 contratos que se pueden generar. La clave es la que viaja en la URL
#: y en el campo oculto "tipo" del formulario.
TIPOS_DE_CONTRATO = {
    "impact_interno": {
        "clase": ContratoImpactOnline,
        "cliente_externo": False,
        "software": "impact",
        "titulo": "Impact Online",
        "subtitulo": "Cliente del Grupo Volvo — Volvo asume el costo",
    },
    "impact_externo": {
        "clase": ContratoImpactOnline,
        "cliente_externo": True,
        "software": "impact",
        "titulo": "Impact Online",
        "subtitulo": "Cliente externo al Grupo Volvo — el Cliente asume el costo",
    },
    "techtool_interno": {
        "clase": ContratoTechTool,
        "cliente_externo": False,
        "software": "techtool",
        "titulo": "TechTool Hardware Independent",
        "subtitulo": "Cliente del Grupo Volvo — Volvo asume el costo",
    },
    "techtool_externo": {
        "clase": ContratoTechTool,
        "cliente_externo": True,
        "software": "techtool",
        "titulo": "TechTool Hardware Independent",
        "subtitulo": "Cliente externo al Grupo Volvo — el Cliente asume el costo",
    },
}

#: Como se le llama a cada campo cuando pydantic lo rechaza. Sin esto, el
#: error mostraria el nombre interno del modelo (ej. "razon_social") en vez
#: de lo que el usuario ve en el formulario.
ETIQUETAS_DE_CAMPO = {
    "razon_social": "Razón social",
    "rut": "RUT",
    "direccion": "Dirección",
    "contacto": "Contacto",
    "representante_legal": "Representante legal",
    "cliente_id": "Partner ID",
    "digipass": "Digipass",
    "partner_id": "Partner ID",
    "cantidad_licencias": "Cantidad de licencias",
}


@app.get("/", response_class=HTMLResponse)
def inicio(request: Request):
    return plantillas_html.TemplateResponse(
        request, "elegir.html", {"tipos": TIPOS_DE_CONTRATO}
    )


@app.get("/nuevo/{tipo}", response_class=HTMLResponse)
def nuevo(request: Request, tipo: str):
    info = TIPOS_DE_CONTRATO.get(tipo)
    if info is None:
        raise HTTPException(status_code=404, detail="Ese tipo de contrato no existe.")

    return plantillas_html.TemplateResponse(
        request,
        "formulario_datos.html",
        {"tipo": tipo, "info": info, "hoy": date.today().isoformat()},
    )


@app.post("/generar", response_class=HTMLResponse)
async def generar(
    request: Request,
    tipo: str = Form(...),
    razon_social: str = Form(""),
    rut: str = Form(""),
    direccion: str = Form(""),
    contacto: str = Form(""),
    representante_legal: str = Form(""),
    fecha: str = Form(""),
    cliente_id: str = Form(""),
    digipass: str = Form("NA"),
    partner_id: str = Form(""),
    cantidad_licencias: str = Form("1"),
):
    info = TIPOS_DE_CONTRATO.get(tipo)
    if info is None:
        raise HTTPException(status_code=404, detail="Ese tipo de contrato no existe.")

    valores = {
        "razon_social": razon_social,
        "rut": rut,
        "direccion": direccion,
        "contacto": contacto,
        "representante_legal": representante_legal,
        "fecha": fecha,
        "cliente_id": cliente_id,
        "digipass": digipass,
        "partner_id": partner_id,
        "cantidad_licencias": cantidad_licencias,
    }

    def con_error(errores: list[str], status_code: int = 400) -> HTMLResponse:
        return plantillas_html.TemplateResponse(
            request,
            "formulario_datos.html",
            {
                "tipo": tipo,
                "info": info,
                "hoy": date.today().isoformat(),
                "valores": valores,
                "errores": errores,
            },
            status_code=status_code,
        )

    try:
        fecha_valor = date.fromisoformat(fecha)
    except ValueError:
        return con_error(["Fecha del contrato: escríbela como AAAA-MM-DD."])

    comunes = dict(fecha=fecha_valor, cliente_externo=info["cliente_externo"])

    try:
        cliente = Cliente(
            razon_social=razon_social,
            rut=rut,
            direccion=direccion,
            contacto=contacto,
            representante_legal=representante_legal,
        )

        if info["software"] == "impact":
            contrato = ContratoImpactOnline(
                cliente=cliente,
                cliente_id=cliente_id.strip(),
                digipass=(digipass or "NA").strip(),
                **comunes,
            )
        else:
            try:
                cantidad = int(cantidad_licencias)
            except ValueError:
                return con_error(["Cantidad de licencias: debe ser un número entero."])
            contrato = ContratoTechTool(
                cliente=cliente,
                partner_id=partner_id.strip(),
                cantidad_licencias=cantidad,
                **comunes,
            )
    except ValidationError as error:
        return con_error(_errores_legibles(error))

    try:
        ruta = generar_docx(contrato, dir_salida=DIR_SALIDA)
    except PlantillaIncompleta as error:
        return con_error([str(error)])

    historial.registrar(
        DIR_HISTORIAL,
        tipo=tipo,
        software=contrato.software,
        cliente_externo=contrato.cliente_externo,
        cliente=contrato.cliente.razon_social,
        rut_cliente=contrato.cliente.rut,
        fecha_contrato=contrato.fecha.strftime("%d-%m-%Y"),
        archivo=ruta.name,
    )

    return plantillas_html.TemplateResponse(
        request, "resultado.html", {"archivo": ruta.name}
    )


@app.get("/historial", response_class=HTMLResponse)
def ver_historial(request: Request, q: str = ""):
    registros = historial.listar(DIR_HISTORIAL, busqueda=q)
    return plantillas_html.TemplateResponse(
        request, "historial.html", {"registros": registros, "busqueda": q}
    )


@app.get("/descargar/{nombre}")
def descargar(nombre: str):
    # Nunca confíes en un nombre de archivo que viene de la URL: alguien podría
    # pedir "../../etc/passwd". Path(nombre).name se queda solo con el nombre.
    ruta = DIR_SALIDA / Path(nombre).name
    if not ruta.exists():
        raise HTTPException(status_code=404, detail="Ese archivo ya no existe.")
    return FileResponse(
        ruta,
        filename=ruta.name,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    )


def _errores_legibles(error: ValidationError) -> list[str]:
    salidas = []
    for detalle in error.errors():
        campo = detalle["loc"][-1] if detalle["loc"] else "?"
        etiqueta = ETIQUETAS_DE_CAMPO.get(str(campo), str(campo))
        mensaje = detalle["msg"].removeprefix("Value error, ")
        salidas.append(f"{etiqueta}: {mensaje}")
    return salidas
