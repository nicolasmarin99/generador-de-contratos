# Contexto del proyecto

Aplicación web que toma un contrato de sublicencia en `.docx`, reemplaza los
datos del cliente por los de otro, y devuelve el documento nuevo conservando
íntegro el texto legal, las tablas y el formato.

Cliente real del problema: contratos de sublicencia de software del Grupo Volvo
(Impact Online y TechTool Hardware Independent) en Chile.

## Cómo se ejecuta

```bash
pip install -r requirements.txt
python servidor.py                 # web en http://127.0.0.1:8000
python -m pytest                   # 29 tests
python scripts/crear_contrato_ejemplo.py   # genera un .docx de prueba
```

## Arquitectura

El código está en capas y **cada una solo conoce a la de adentro**:

```
web/app.py  →  src/contratos/{reemplazo,deteccion,campos,validadores}.py
main.py     →  src/contratos/{cli,motor,modelos}.py
```

`src/contratos/` es el dominio y no sabe que existe HTTP. Si una tarea pide
tocar reglas de negocio, van ahí, no en `web/app.py`. `web/app.py` solo traduce
peticiones HTTP a llamadas al dominio y devuelve HTML.

| Archivo | Responsabilidad |
|---|---|
| `campos.py` | Fuente de verdad única de qué campos existen. El detector y el formulario lo leen de aquí. |
| `deteccion.py` | Lee los valores actuales del documento subido para precargar el formulario. |
| `reemplazo.py` | Sustituye texto en el `.docx` sin romper las runs de Word. |
| `validadores.py` | RUT chileno, módulo 11. |
| `modelos.py` / `motor.py` | Modo alternativo con plantillas `{{ }}`, usado solo por la CLI. |

## Invariantes que no se deben romper

1. **Los reemplazos se ordenan de más largo a más corto** (`reemplazo.aplicar`).
   Si se quita ese `sort`, reemplazar `"ciudad de Santiago"` antes que
   `"Gran Américas Santiago Chile S.A."` mutila el nombre. Hay un test que lo
   cubre: `test_el_valor_largo_se_procesa_antes_que_el_corto`.

2. **Nunca usar `parrafo.text.replace()`.** Word parte los párrafos en varias
   `<w:r>` (runs), así que el texto buscado puede no existir como cadena
   contigua. Se recorre la concatenación de runs y se sustituye por tramos; ver
   `_sustituir` en `reemplazo.py`.

3. **Recorrer todo el documento**, no solo `document.paragraphs`: también
   tablas, tablas anidadas, encabezados y pies. Ver `_todos_los_parrafos`.

4. **El reporte de reemplazos es funcional, no decorativo.** Cada `Reemplazo`
   cuenta sus aplicaciones y la vista de resultado las muestra. Un cambio con
   `veces == 0` significa que el documento quedó con el dato antiguo, y el
   usuario tiene que verlo.

5. **Agregar un campo se hace solo en `campos.py`.** Formulario y detección se
   derivan de ahí. Si una tarea obliga a tocar tres archivos para un campo
   nuevo, el diseño se rompió.

## Convenciones

- Código, comentarios y nombres en español. Los identificadores no llevan tilde.
- Los comentarios explican **por qué**, no qué hace la línea.
- Todo cambio en `reemplazo.py` necesita un test en `tests/test_reemplazo.py`.
  Es la parte que puede fallar en silencio y entregar un contrato con datos del
  cliente anterior.
- Sin frameworks de frontend: HTML server-rendered con Jinja2 y CSS plano.
- Este es un proyecto de aprendizaje. Al proponer cambios, explicar el
  razonamiento y las alternativas descartadas, no solo entregar el código.

## Pendientes

- Borrado automático de los archivos en `subidas/` (hoy se acumulan).
- Historial de contratos generados.
- Despliegue.
