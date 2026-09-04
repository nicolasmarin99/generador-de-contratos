# -*- mode: python ; coding: utf-8 -*-
"""Empaqueta el generador de contratos como ejecutable de escritorio.

Modo "onedir" a proposito (una carpeta con el .exe adentro, no un solo
archivo): asi plantillas/, salida/ y historial/ quedan como carpetas
normales al lado del .exe -- visibles, editables, y sin la demora de
descomprimir un .exe "onefile" en una carpeta temporal cada vez que se abre.

Construir:  pyinstaller escritorio.spec
Resultado:  dist/GeneradorContratos/GeneradorContratos.exe
"""

DATOS = [
    ("web/templates", "web/templates"),
    ("web/static", "web/static"),
    ("plantillas/impact/interno.docx", "plantillas/impact"),
    ("plantillas/impact/externo.docx", "plantillas/impact"),
    ("plantillas/techtool/interno.docx", "plantillas/techtool"),
    ("plantillas/techtool/externo.docx", "plantillas/techtool"),
]

# uvicorn resuelve algunos modulos por nombre en tiempo de ejecucion (loop y
# protocolo "auto"), lo que el analisis estatico de PyInstaller no rastrea
# solo. Sin esto el .exe arranca y se cae al primer request.
HIDDEN_IMPORTS = [
    "uvicorn.logging",
    "uvicorn.loops",
    "uvicorn.loops.auto",
    "uvicorn.loops.asyncio",
    "uvicorn.protocols",
    "uvicorn.protocols.http",
    "uvicorn.protocols.http.auto",
    "uvicorn.protocols.http.h11_impl",
    "uvicorn.protocols.websockets",
    "uvicorn.protocols.websockets.auto",
    "uvicorn.protocols.utils",
    "uvicorn.lifespan",
    "uvicorn.lifespan.on",
]

analisis = Analysis(
    ["escritorio.py"],
    pathex=["src", "web"],
    datas=DATOS,
    hiddenimports=HIDDEN_IMPORTS,
    noarchive=False,
)

pyz = PYZ(analisis.pure)

exe = EXE(
    pyz,
    analisis.scripts,
    [],
    exclude_binaries=True,
    name="GeneradorContratos",
    console=True,
    # Sin esto, PyInstaller 6+ mete plantillas/web/etc. dentro de una
    # subcarpeta _internal en vez de dejarlas al lado del .exe.
    contents_directory=".",
)

COLLECT(
    exe,
    analisis.binaries,
    analisis.datas,
    name="GeneradorContratos",
)
