"""Arranca la aplicacion web.

Uso:  python servidor.py
Luego abre http://127.0.0.1:8000 en el navegador.
"""

import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
sys.path.insert(0, str(RAIZ / "src"))
sys.path.insert(0, str(RAIZ / "web"))

import uvicorn  # noqa: E402

if __name__ == "__main__":
    print("Servidor en http://127.0.0.1:8000  (Ctrl+C para detener)")
    uvicorn.run(
        "app:app",
        host="127.0.0.1",
        port=8000,
        reload=True,
        reload_dirs=[str(RAIZ / "web"), str(RAIZ / "src")],
    )
