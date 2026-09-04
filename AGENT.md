# Contexto del proyecto

Aplicación que genera contratos de sublicencia en `.docx` a partir de una
plantilla legal oficial (con marcadores `{{ }}`) y los datos del cliente. El
usuario elige el tipo de contrato, completa un formulario, y descarga el
documento con el texto legal exacto de esa plantilla.

Cliente real del problema: contratos de sublicencia de software del Grupo Volvo
(Impact Online y TechTool Hardware Independent) en Chile, cada uno con dos
variantes según quién asume el costo: el cliente es del Grupo Volvo (interno)
o es un cliente externo al grupo (externo). Son 4 plantillas en total.

## Cómo se ejecuta

```bash
pip install -r requirements-dev.txt   # requirements.txt + herramientas de test/build
python servidor.py                    # web en http://127.0.0.1:8000, con recarga
python -m pytest                      # 59 tests
pyinstaller escritorio.spec           # arma el ejecutable de escritorio (dist/GeneradorContratos/)
```

## Arquitectura

El código está en capas y **cada una solo conoce a la de adentro**:

```
web/app.py  →  src/contratos/{modelos,motor,historial,rutas}.py  →  validadores.py
main.py     →  src/contratos/{cli,motor,modelos}.py               (el mismo motor)
```

`src/contratos/` es el dominio y no sabe que existe HTTP. Si una tarea pide
tocar reglas de negocio, van ahí, no en `web/app.py`. `web/app.py` solo traduce
peticiones HTTP a llamadas al dominio y devuelve HTML.

| Archivo | Responsabilidad |
|---|---|
| `modelos.py` | `Cliente`, `Sublicenciante`, y un modelo por software (`ContratoImpactOnline`, `ContratoTechTool`). `cliente_externo: bool` decide cuál de las 2 plantillas de ese software se usa. |
| `motor.py` | Renderiza una plantilla `.docx` con `docxtpl` usando el contexto del modelo. Falla si la plantilla pide un marcador que el modelo no tiene. |
| `historial.py` | Sqlite local (`historial/historial.db`) con cada contrato generado: cuándo, cliente, RUT, archivo. Recibe la carpeta como parámetro (nunca la resuelve sola) para que los tests puedan aislarla. |
| `rutas.py` | `raiz_app()`: dónde viven `plantillas/`, `salida/`, `historial/` y `web/`. Es la carpeta del proyecto en modo fuente, o la carpeta del `.exe` cuando corre empaquetado (`sys.frozen`). |
| `validadores.py` | RUT chileno, módulo 11. |
| `reemplazo.py` | Sustituye texto en un `.docx` respetando las runs de Word. Ya no lo usa el flujo en vivo (las plantillas están pre-marcadas); se usó para migrar los contratos reales a `{{ marcadores }}` y sigue teniendo tests porque es lógica delicada, no muerta. |

`escritorio.py` es la puerta de entrada que PyInstaller empaqueta: igual que
`servidor.py` pero sin recarga automática y abriendo el navegador solo.

## Invariantes que no se deben romper

1. **Un campo de la plantilla se agrega solo en `modelos.py`** (el modelo y su
   `contexto()`). Si `motor.py` se queja de un marcador que falta, es que la
   plantilla `.docx` pide algo que el modelo todavía no expone — se agrega ahí,
   no se parchea en `web/app.py`.

2. **`historial.py` y `rutas.py` reciben la carpeta como parámetro**, nunca la
   calculan ellos mismos a partir de rutas fijas. Es lo que permite testear con
   `tmp_path` sin tocar el `historial/` ni el `salida/` reales — y lo que
   permite que el mismo código sirva en modo fuente y en el `.exe`.

3. **`web/app.py` no debe llamar a `generar_docx()` sin pasar `dir_salida`
   explícito.** Si se le pasa el default de `motor.py`, siempre escribe en el
   `salida/` del proyecto real, incluso en los tests — así se rompió una vez
   (ver `tests/test_web_app.py`, fixture `cliente_http`).

4. **Nunca usar `parrafo.text.replace()` sobre un `.docx`** en `reemplazo.py`:
   Word parte los párrafos en varias `<w:r>` (runs), así que el texto buscado
   puede no existir como cadena contigua. Ver `_sustituir`.

## Convenciones

- Código, comentarios y nombres en español. Los identificadores no llevan tilde.
- Los comentarios explican **por qué**, no qué hace la línea.
- Sin frameworks de frontend: HTML server-rendered con Jinja2 y CSS plano.
- Este es un proyecto de aprendizaje. Al proponer cambios, explicar el
  razonamiento y las alternativas descartadas, no solo entregar el código.

## Pendientes

- Despliegue (hoy es local: web en `127.0.0.1` o el `.exe` de escritorio).
