"""Historial de contratos generados en este equipo.

Cada vez que se genera un contrato se guarda un registro aqui: quien, que
tipo de contrato, cuando (fecha y hora). Vive en un sqlite (historial.db)
dentro de la carpeta que le pases -- normalmente `raiz_app() / "historial"`,
igual que salida/ y plantillas/ viven bajo esa misma raiz.

Recibe la carpeta como parametro en vez de resolverla aqui adentro para que
los tests puedan apuntar a una carpeta temporal sin tocar el historial real.
"""

import sqlite3
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

NOMBRE_BD = "historial.db"


@dataclass(frozen=True)
class Registro:
    """Una fila del historial, ya lista para mostrar en la web."""

    id: int
    creado_en: datetime
    tipo: str
    software: str
    cliente_externo: bool
    cliente: str
    rut_cliente: str
    fecha_contrato: str
    archivo: str


def _conectar(dir_historial: Path) -> sqlite3.Connection:
    dir_historial.mkdir(parents=True, exist_ok=True)
    conexion = sqlite3.connect(dir_historial / NOMBRE_BD)
    conexion.row_factory = sqlite3.Row
    conexion.execute(
        """
        CREATE TABLE IF NOT EXISTS contratos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creado_en TEXT NOT NULL,
            tipo TEXT NOT NULL,
            software TEXT NOT NULL,
            cliente_externo INTEGER NOT NULL,
            cliente TEXT NOT NULL,
            rut_cliente TEXT NOT NULL,
            fecha_contrato TEXT NOT NULL,
            archivo TEXT NOT NULL
        )
        """
    )
    return conexion


def registrar(
    dir_historial: Path,
    *,
    tipo: str,
    software: str,
    cliente_externo: bool,
    cliente: str,
    rut_cliente: str,
    fecha_contrato: str,
    archivo: str,
) -> Registro:
    """Guarda un contrato recien generado y devuelve el registro creado."""
    creado_en = datetime.now().isoformat(timespec="seconds")
    with closing(_conectar(dir_historial)) as conexion:
        cursor = conexion.execute(
            """
            INSERT INTO contratos
                (creado_en, tipo, software, cliente_externo, cliente,
                 rut_cliente, fecha_contrato, archivo)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                creado_en,
                tipo,
                software,
                int(cliente_externo),
                cliente,
                rut_cliente,
                fecha_contrato,
                archivo,
            ),
        )
        conexion.commit()
        id_nuevo = cursor.lastrowid

    return Registro(
        id=id_nuevo,
        creado_en=datetime.fromisoformat(creado_en),
        tipo=tipo,
        software=software,
        cliente_externo=cliente_externo,
        cliente=cliente,
        rut_cliente=rut_cliente,
        fecha_contrato=fecha_contrato,
        archivo=archivo,
    )


def listar(dir_historial: Path, *, busqueda: str = "") -> list[Registro]:
    """Devuelve los contratos generados, mas reciente primero.

    Si `busqueda` no esta vacia, filtra por cliente, RUT, software o nombre
    de archivo (sin distinguir mayusculas ni exigir coincidencia exacta).
    """
    with closing(_conectar(dir_historial)) as conexion:
        texto = busqueda.strip()
        if texto:
            patron = f"%{texto}%"
            filas = conexion.execute(
                """
                SELECT * FROM contratos
                WHERE cliente LIKE ? COLLATE NOCASE
                   OR rut_cliente LIKE ?
                   OR software LIKE ? COLLATE NOCASE
                   OR archivo LIKE ? COLLATE NOCASE
                ORDER BY id DESC
                """,
                (patron, patron, patron, patron),
            ).fetchall()
        else:
            filas = conexion.execute("SELECT * FROM contratos ORDER BY id DESC").fetchall()

    return [
        Registro(
            id=fila["id"],
            creado_en=datetime.fromisoformat(fila["creado_en"]),
            tipo=fila["tipo"],
            software=fila["software"],
            cliente_externo=bool(fila["cliente_externo"]),
            cliente=fila["cliente"],
            rut_cliente=fila["rut_cliente"],
            fecha_contrato=fila["fecha_contrato"],
            archivo=fila["archivo"],
        )
        for fila in filas
    ]
