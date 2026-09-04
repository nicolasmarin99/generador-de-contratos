"""El motor: toma una plantilla y un contexto y produce el documento.

Es la pieza que NUNCA cambia cuando entra un cliente nuevo ni cuando el
abogado corrige una clausula. Si te encuentras editando este archivo por
esas razones, algo esta mal disenado.
"""

import shutil
import subprocess
from pathlib import Path

from docxtpl import DocxTemplate

from .modelos import ContratoBase
from .rutas import raiz_app

RAIZ = raiz_app()
DIR_PLANTILLAS = RAIZ / "plantillas"
DIR_SALIDA = RAIZ / "salida"


class PlantillaIncompleta(RuntimeError):
    """La plantilla pide marcadores que el contexto no trae."""


def marcadores_de(ruta_plantilla: Path) -> set[str]:
    """Lista los marcadores {{ }} que aparecen en la plantilla.

    Sirve para dos cosas: verificar que marcaste bien el .docx, y detectar
    faltantes antes de generar un documento a medio llenar.
    """
    plantilla = DocxTemplate(ruta_plantilla)
    return plantilla.get_undeclared_template_variables()


def generar_docx(
    contrato: ContratoBase,
    dir_plantillas: Path = DIR_PLANTILLAS,
    dir_salida: Path = DIR_SALIDA,
    estricto: bool = True,
) -> Path:
    """Renderiza el contrato y devuelve la ruta del .docx generado."""
    ruta_plantilla = dir_plantillas / contrato.plantilla
    if not ruta_plantilla.exists():
        raise FileNotFoundError(f"No encuentro la plantilla: {ruta_plantilla}")

    contexto = contrato.contexto()

    if estricto:
        faltantes = marcadores_de(ruta_plantilla) - set(contexto)
        if faltantes:
            raise PlantillaIncompleta(
                "La plantilla pide marcadores que no estan en el contexto: "
                + ", ".join(sorted(faltantes))
            )

    plantilla = DocxTemplate(ruta_plantilla)
    plantilla.render(contexto)

    dir_salida.mkdir(parents=True, exist_ok=True)
    nombre = _nombre_archivo(contrato)
    destino = dir_salida / f"{nombre}.docx"
    plantilla.save(destino)
    return destino


def exportar_pdf(ruta_docx: Path) -> Path:
    """Convierte el .docx a PDF usando LibreOffice en modo headless.

    Se apoya en un proceso externo a proposito: reimplementar el layout de
    Word en Python es un pozo sin fondo, y LibreOffice ya lo hace bien.
    """
    soffice = shutil.which("soffice") or shutil.which("libreoffice")
    if soffice is None:
        raise RuntimeError(
            "LibreOffice no esta instalado. Instalalo o desactiva la exportacion a PDF."
        )

    subprocess.run(
        [
            soffice,
            "--headless",
            "--convert-to",
            "pdf",
            "--outdir",
            str(ruta_docx.parent),
            str(ruta_docx),
        ],
        check=True,
        capture_output=True,
        timeout=120,
    )
    return ruta_docx.with_suffix(".pdf")


def _nombre_archivo(contrato: ContratoBase) -> str:
    """Nombre predecible y ordenable: 2026-07-22_impact-interno_gran-americas"""
    ruta_plantilla = Path(contrato.plantilla)
    tipo = f"{ruta_plantilla.parent.name}-{ruta_plantilla.stem}"
    empresa = (
        contrato.cliente.razon_social.lower()
        .replace(" ", "-")
        .replace(".", "")
        .replace(",", "")
    )
    return f"{contrato.fecha.isoformat()}_{tipo}_{empresa}"
