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

import socket
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
PUERTO_PREFERIDO = 8000
PUERTOS_A_PROBAR = 20


def puerto_libre(host: str = HOST, desde: int = PUERTO_PREFERIDO) -> int:
    """Devuelve el primer puerto libre a partir de `desde`.

    Sin esto, abrir la app con el puerto 8000 ocupado (otra instancia ya
    abierta, u otro programa) la mata con un error de socket y la ventana se
    cierra sola: el usuario ve un parpadeo y nada mas.
    """
    for puerto in range(desde, desde + PUERTOS_A_PROBAR):
        # Ojo: nada de SO_REUSEADDR aqui. En Windows esa opcion permite
        # bindear un puerto que YA esta en uso, asi que el sondeo diria
        # "libre" y uvicorn -- que bindea sin ella -- moriria igual. El
        # sondeo tiene que hacer exactamente lo mismo que hara uvicorn.
        with socket.socket() as prueba:
            try:
                prueba.bind((host, puerto))
            except OSError:
                continue
            return puerto

    raise SystemExit(
        f"No encontre un puerto libre entre {desde} y {desde + PUERTOS_A_PROBAR - 1}. "
        "Cierra la aplicacion si ya la tienes abierta y vuelve a intentarlo."
    )


def _abrir_navegador(url: str) -> None:
    webbrowser.open(url)


if __name__ == "__main__":
    puerto = puerto_libre()
    url = f"http://{HOST}:{puerto}"

    if puerto != PUERTO_PREFERIDO:
        print(f"El puerto {PUERTO_PREFERIDO} estaba ocupado, uso el {puerto}.")
    print(f"Generador de contratos: {url}  (cierra esta ventana para detenerlo)")

    threading.Timer(1.0, _abrir_navegador, args=(url,)).start()
    uvicorn.run(aplicacion, host=HOST, port=puerto)
