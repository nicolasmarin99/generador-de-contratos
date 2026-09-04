---
trigger: always_on
description: Reglas del generador de contratos
---

# Reglas de trabajo

Lee `AGENT.md` en la raíz antes de proponer cambios: ahí están la arquitectura
por capas y los invariantes del reemplazo de texto.

## No romper

- No sustituir el `sort` por longitud en `reemplazo.aplicar`.
- No usar `parrafo.text.replace()` sobre un `.docx`: rompe con las runs de Word.
- No poner reglas de negocio en `web/app.py`. Van en `src/contratos/`.
- No agregar un campo del contrato fuera de `src/contratos/campos.py`.

## Al terminar una tarea

- Ejecutar `python -m pytest` y dejarlo en verde.
- Si se tocó `reemplazo.py` o `deteccion.py`, agregar el test correspondiente.

## Tono

Proyecto de aprendizaje de un estudiante de ingeniería informática. Explicar el
porqué de cada decisión y qué alternativas se descartaron, en español.
