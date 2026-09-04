"""Donde vive todo: plantillas/, salida/, historial/ y web/.

Corriendo desde el codigo fuente (`python servidor.py`), la raiz es la
carpeta del proyecto. Empaquetado como ejecutable de escritorio con
PyInstaller, `sys.frozen` queda en True y el codigo corre embebido en el
.exe -- por eso ahi la raiz pasa a ser la carpeta que CONTIENE al .exe.

Esto es lo que hace que plantillas/salida/historial queden siempre al lado
de donde se ejecuta la app (visibles, editables, y persistentes si se
reinstala), en vez de escondidos en una carpeta temporal. build.spec copia
web/templates, web/static y las 4 plantillas oficiales a esa misma
estructura de carpetas dentro del build, para que ambos modos (fuente y
empaquetado) resuelvan las mismas rutas relativas.
"""

import sys
from pathlib import Path


def raiz_app() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent
    # Este archivo vive en src/contratos/rutas.py -> subir dos niveles.
    return Path(__file__).resolve().parents[2]
