---
trigger: always_on
description: Reglas del generador de contratos
---

# Reglas de trabajo

Lee `AGENT.md` en la raíz antes de proponer cambios: ahí están la arquitectura
por capas y los invariantes del reemplazo de texto.

## No romper

- No usar `parrafo.text.replace()` sobre un `.docx`: rompe con las runs de Word.
- No poner reglas de negocio en `web/app.py`. Van en `src/contratos/`.
- No agregar un campo del contrato fuera de `src/contratos/modelos.py`.
- No llamar a `generar_docx()` desde `web/app.py` sin pasar `dir_salida`
  explícito (si no, ignora el `DIR_SALIDA` de la web y escribe en el `salida/`
  real del proyecto, incluso durante los tests).
- `historial.py` y `rutas.py` reciben la carpeta de trabajo como parámetro;
  no deben resolverla ellos mismos con una ruta fija.

## Al terminar una tarea

- Ejecutar `python -m pytest` y dejarlo en verde (requiere
  `pip install -r requirements-dev.txt`, por `httpx`/`TestClient`).
- Si se tocó `reemplazo.py`, `historial.py` o `rutas.py`, agregar el test
  correspondiente.

## Tono

Proyecto de aprendizaje de un estudiante de ingeniería informática. Explicar el
porqué de cada decisión y qué alternativas se descartaron, en español.
