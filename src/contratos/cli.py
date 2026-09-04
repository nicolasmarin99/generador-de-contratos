"""Interfaz de linea de comandos.

Es la capa mas externa: traduce argumentos de terminal a llamadas al dominio.
No contiene ninguna regla de negocio. Cuando montemos la web, el modulo web
hara exactamente lo mismo traduciendo un formulario HTTP, y reutilizara
motor.py y modelos.py sin cambiarles una linea.
"""

import argparse
import json
import sys
from pathlib import Path

from .modelos import TIPOS_DE_CONTRATO
from .motor import exportar_pdf, generar_docx


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="contratos",
        description="Genera contratos de sublicencia a partir de una plantilla y un JSON.",
    )
    parser.add_argument(
        "tipo",
        choices=sorted(TIPOS_DE_CONTRATO),
        help="Que contrato generar",
    )
    parser.add_argument("datos", type=Path, help="Ruta al JSON con los datos del cliente")
    parser.add_argument("--pdf", action="store_true", help="Exportar tambien a PDF")

    args = parser.parse_args(argv)

    try:
        crudo = json.loads(args.datos.read_text(encoding="utf-8"))
    except FileNotFoundError:
        print(f"No encuentro el archivo de datos: {args.datos}", file=sys.stderr)
        return 1
    except json.JSONDecodeError as error:
        print(f"El JSON tiene un error de sintaxis: {error}", file=sys.stderr)
        return 1

    Contrato = TIPOS_DE_CONTRATO[args.tipo]

    try:
        contrato = Contrato(**crudo)
    except Exception as error:  # pydantic.ValidationError y validadores propios
        print("Los datos no pasaron la validacion:", file=sys.stderr)
        print(error, file=sys.stderr)
        return 1

    docx = generar_docx(contrato)
    print(f"Generado: {docx}")

    if args.pdf:
        pdf = exportar_pdf(docx)
        print(f"Generado: {pdf}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
