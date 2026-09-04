"""Atajo para inspeccionar una plantilla sin pelear con PYTHONPATH.

Uso:  python inspeccionar.py plantillas/impact_online.docx
"""

import runpy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent / "src"))
runpy.run_path(
    str(Path(__file__).resolve().parent / "scripts" / "inspeccionar_plantilla.py"),
    run_name="__main__",
)
