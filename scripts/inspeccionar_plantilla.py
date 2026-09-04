"""Lista los marcadores {{ }} que docxtpl detecta en una plantilla.

Esta es tu herramienta de diagnostico al marcar los .docx reales. Si escribes
{{ cliente }} en Word y aqui no aparece, significa que Word partio el texto en
varias "runs" internas y el marcador quedo roto.

Uso:  python scripts/inspeccionar_plantilla.py plantillas/impact_online.docx
"""

import sys
from pathlib import Path

from docxtpl import DocxTemplate


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__)
        return 1

    ruta = Path(sys.argv[1])
    if not ruta.exists():
        print(f"No encuentro: {ruta}")
        return 1

    marcadores = sorted(DocxTemplate(ruta).get_undeclared_template_variables())

    if not marcadores:
        print(f"{ruta.name}: no se detecto ningun marcador.")
        print("Revisa que hayas escrito {{ nombre }} y que Word no lo haya partido.")
        return 1

    print(f"{ruta.name}: {len(marcadores)} marcadores detectados\n")
    for marcador in marcadores:
        print(f"  - {marcador}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
