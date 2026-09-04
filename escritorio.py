"""Punto de entrada del ejecutable de escritorio.

A diferencia de servidor.py (modo desarrollo: recarga automatica al guardar
un archivo), este es el que PyInstaller empaqueta en el .exe: arranca el
servidor tal cual va a quedar en produccion, sin recarga, y abre el
navegador solo para que quien lo use no tenga que escribir la URL a mano.

Importa el objeto FastAPI directamente (`from app import app`) en vez de
pasarle un string "app:app" a uvicorn. Un import normal es lo que
PyInstaller puede rastrear en el analisis estatico; un string generado en
tiempo de ejecucion no.
"""

import sys
import threading
import webbrowser
from pathlib import Path

if not getattr(sys, "frozen", False):
    RAIZ = Path(__file__).resolve().parent
    sys.path.insert(0, str(RAIZ / "src"))
    sys.path.insert(0, str(RAIZ / "web"))

import uvicorn  # noqa: E402
from app import app as aplicacion  # noqa: E402

HOST = "127.0.0.1"
PUERTO = 8000


def _abrir_navegador() -> None:
    webbrowser.open(f"http://{HOST}:{PUERTO}")


if __name__ == "__main__":
    print(f"Generador de contratos: http://{HOST}:{PUERTO}  (cierra esta ventana para detenerlo)")
    threading.Timer(1.0, _abrir_navegador).start()
    uvicorn.run(aplicacion, host=HOST, port=PUERTO)
