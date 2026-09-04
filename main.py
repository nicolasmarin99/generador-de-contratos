"""Punto de entrada del proyecto.

Existe para que puedas ejecutar todo con `python main.py ...` sin pelear con
variables de entorno. Lo unico que hace es avisarle a Python que el codigo
vive en la carpeta src/ y despues ceder el control a la CLI real.

Uso:
    python main.py impact datos/clientes/gran-americas.json
    python main.py impact datos/clientes/gran-americas.json --pdf
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))

from contratos.cli import main  # noqa: E402

if __name__ == "__main__":
    raise SystemExit(main())
