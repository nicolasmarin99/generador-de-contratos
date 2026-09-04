# Generador de contratos de sublicencia

Genera contratos en `.docx` (y opcionalmente `.pdf`) a partir de una plantilla
Word y un archivo de datos del cliente. El texto legal se escribe una vez; lo
único que cambia entre un contrato y otro son los datos.

## Por qué existe

Redactar cada contrato copiando el anterior y reemplazando datos a mano es lento
y propenso a errores: se olvida un RUT, queda el nombre del cliente anterior en
la cláusula 12, se cae un dígito. Este proyecto convierte ese trabajo manual en
una operación reproducible y verificable.

## Estructura del proyecto

```
generador-contratos/
├── servidor.py           # Arranca la web (modo desarrollo, con recarga)
├── escritorio.py         # Arranca la web (modo ejecutable: lo empaqueta PyInstaller)
├── escritorio.spec       # Receta de empaquetado (pyinstaller escritorio.spec)
├── main.py               # Arranca la CLI
├── src/contratos/        # El dominio: no sabe que existe HTTP
│   ├── validadores.py    #   Reglas: qué es un RUT válido
│   ├── reemplazo.py      #   Sustituir texto sin romper las runs de Word
│   ├── modelos.py        #   Forma de un cliente y de cada tipo de contrato
│   ├── motor.py          #   Fusionar plantilla + datos con docxtpl
│   ├── historial.py      #   Guarda y busca los contratos ya generados (sqlite)
│   ├── rutas.py          #   Donde vive todo: fuente vs. ejecutable empaquetado
│   └── cli.py            #   Entrada por terminal
├── web/                  # La interfaz web
│   ├── app.py            #   Rutas HTTP
│   ├── templates/        #   HTML
│   └── static/           #   CSS
├── plantillas/            # Las 4 plantillas oficiales, con {{ marcadores }}
│   ├── impact/interno.docx    #   Impact Online, cliente del Grupo Volvo
│   ├── impact/externo.docx    #   Impact Online, cliente externo
│   ├── techtool/interno.docx  #   TechTool, cliente del Grupo Volvo
│   └── techtool/externo.docx  #   TechTool, cliente externo
├── salida/               # Documentos generados
├── historial/             # historial.db (sqlite): quién generó qué y cuándo
├── ejemplos/             # Contrato de prueba
├── scripts/              # Utilidades
└── tests/                # Verificación automática
```

La regla de oro: **cada capa solo conoce a la de adentro**. `cli.py` usa
`motor.py`, que usa `modelos.py`, que usa `validadores.py`. Nunca al revés. Por
eso agregar una interfaz web después no obliga a tocar nada de lo anterior.

## Abrir en un IDE

El proyecto trae configuración lista para VS Code, Cursor y Google Antigravity
(los tres comparten el formato `.vscode/`):

- `.vscode/launch.json` — configuraciones de depuración: levantar la web, correr
  la CLI, ejecutar los tests. Se lanzan con F5.
- `.vscode/settings.json` — le dice al IDE que el código vive en `src/` y `web/`,
  para que no marque como error los `from contratos import ...`.
- `.vscode/tasks.json` — tareas frecuentes desde la paleta de comandos.
- `AGENT.md` y `.agent/rules/` — contexto del proyecto para los agentes del IDE:
  arquitectura, invariantes y qué no romper.

Después de abrir la carpeta, selecciona el intérprete de `.venv` con
`Ctrl+Shift+P` → *Python: Select Interpreter*.

## Instalación

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

Para correr los tests o armar el ejecutable de escritorio, instala además las
dependencias de desarrollo (incluye las de arriba):

```bash
pip install -r requirements-dev.txt
```

## Cómo se usa (aplicación web)

```bash
python servidor.py
```

Abre <http://127.0.0.1:8000> y sigue tres pasos:

1. **Eliges el tipo de contrato**: Impact Online o TechTool, cliente del Grupo
   Volvo o cliente externo. Esa elección carga la plantilla oficial exacta
   (con la cláusula de costos ya redactada según quién la asume) — nunca se
   sube un documento.
2. **Completas los datos** del cliente (razón social, RUT, dirección,
   contacto, representante legal, fecha, y el dato propio del software:
   Partner ID para Impact, o Partner ID + cantidad de licencias para
   TechTool).
3. **Descargas** el `.docx` generado: el texto legal completo de la plantilla,
   con esos datos insertados.

La CLI usa el mismo motor y comparte el mismo validador de RUT:
`python main.py impact datos/clientes/gran-americas.json`. La diferencia es
solo la interfaz: la CLI lee un JSON, la web lee un formulario.

## Historial

Cada contrato generado (desde la web o el ejecutable) queda registrado en
`historial/historial.db` — un sqlite local a este equipo, no una base de
datos compartida. En <http://127.0.0.1:8000/historial> se ve la lista
completa (fecha y hora, software, cliente, RUT, archivo) con un buscador que
filtra por cliente, RUT o software. El botón "Descargar" de cada fila reusa
la ruta `/descargar/{archivo}`, así que sigue funcionando mientras el `.docx`
no se haya borrado de `salida/`.

## Ejecutable de escritorio

Para no depender de tener Python instalado, `escritorio.py` empaqueta la
misma app web en un `.exe` que abre el navegador solo al arrancar:

```bash
pip install -r requirements-dev.txt
pyinstaller escritorio.spec
```

El resultado queda en `dist/GeneradorContratos/`. Es modo "onedir" a
propósito (una carpeta con el `.exe` y sus archivos al lado, no un solo
archivo comprimido): `plantillas/`, `web/`, `salida/` e `historial/` quedan
como carpetas normales junto al ejecutable — se pueden editar las plantillas
sin reconstruir el `.exe`, y `salida/`/`historial/` sobreviven aunque se
reemplace el ejecutable por una versión nueva. Para distribuirlo, comprime y
comparte toda la carpeta `dist/GeneradorContratos/`, no solo el `.exe`.

`escritorio.py` es distinto de `servidor.py`: no usa recarga automática (no
tiene sentido en un `.exe` ya construido), abre el navegador por su cuenta y
busca un puerto libre a partir del 8000 (si ya tienes la app abierta, u otro
programa ocupa ese puerto, usa el 8001 y así; sin eso el `.exe` moría con un
error de socket y la ventana se cerraba sola).
`src/contratos/rutas.py` es lo que hace que ambos modos —código fuente y
`.exe`— resuelvan las mismas rutas relativas (`plantillas/`, `salida/`,
`historial/`): detecta si está corriendo empaquetado (`sys.frozen`) y en ese
caso usa la carpeta del ejecutable como raíz, en vez de la carpeta del
proyecto.

## Cómo marcar tus plantillas reales

Este es el paso manual del proyecto y el único que no se puede automatizar.
Hay 4 plantillas, una por combinación de software y tipo de cliente:

| Plantilla | Software | Cliente |
|---|---|---|
| `plantillas/impact/interno.docx` | Impact Online | Grupo Volvo (Volvo asume el costo) |
| `plantillas/impact/externo.docx` | Impact Online | Externo (el Cliente asume el costo) |
| `plantillas/techtool/interno.docx` | TechTool | Grupo Volvo (Volvo asume el costo) |
| `plantillas/techtool/externo.docx` | TechTool | Externo (el Cliente asume el costo) |

Para marcar una:

1. Abre el contrato real en Word.
2. Reemplaza cada dato variable por su marcador: donde dice
   `Gran Américas Santiago Chile S.A.` escribe `{{ cliente }}`.
3. Guarda con el nombre que corresponda de la tabla de arriba.
4. Verifica que los marcadores hayan quedado bien:

```bash
PYTHONPATH=src python scripts/inspeccionar_plantilla.py plantillas/impact/interno.docx
```

### El problema de las "runs" de Word

Si escribiste `{{ cliente }}` y el inspector no lo detecta, la causa casi
siempre es la misma. Word no guarda un párrafo como una cadena continua: lo
parte en fragmentos llamados *runs* cada vez que cambia el formato, o cuando el
corrector ortográfico deja una marca. Por dentro, tu marcador puede haber
quedado así:

```xml
<w:r><w:t>{{ cli</w:t></w:r><w:r><w:t>ente }}</w:t></w:r>
```

Para docxtpl eso no es un marcador, es texto suelto.

Solución: borra el marcador completo, escríbelo de una sola pasada sin mover el
cursor al medio, y evita aplicar negrita o cambiar la fuente dentro de las
llaves. Si sigue partido, escríbelo en un editor de texto plano, cópialo y pégalo
en Word con *Pegar sin formato* (Ctrl+Shift+V).

## Marcadores disponibles

| Marcador | Contenido | Contrato |
|---|---|---|
| `{{ cliente }}` | Razón social del cliente | Ambos |
| `{{ rut_cliente }}` | RUT del cliente, ya formateado | Ambos |
| `{{ direccion_cliente }}` | Dirección del cliente | Ambos |
| `{{ contacto }}` | Persona de contacto | Ambos |
| `{{ representante_legal }}` | Representante legal | Ambos |
| `{{ sublicenciante }}` | Empresa del Grupo Volvo | Ambos |
| `{{ rut_sublicenciante }}` | RUT del sublicenciante | Ambos |
| `{{ direccion_sublicenciante }}` | Dirección del sublicenciante | Ambos |
| `{{ fecha }}` | Fecha del contrato (dd-mm-aaaa) | Ambos |
| `{{ software }}` | Nombre del software | Ambos |
| `{{ cliente_id }}` | Partner ID (Impact usa este nombre de campo internamente) | Impact Online |
| `{{ digipass }}` | Digipass | Impact Online |
| `{{ partner_id }}` | Partner ID | TechTool |
| `{{ cantidad_licencias }}` | Número de licencias | TechTool |

Si agregas un marcador nuevo a una plantilla, el motor se niega a generar el
documento hasta que ese campo exista en el modelo. Es intencional: prefiere
fallar a entregar un contrato con un `{{ }}` visible.

Ninguno de estos marcadores decide **qué plantilla** se usa — eso lo decide
`cliente_externo` (`true`/`false`), que no se imprime en el documento: solo
selecciona cuál de las dos plantillas (interno/externo) de ese software se
renderiza. Por eso no aparece en esta tabla.

## Tests

```bash
pip install -r requirements-dev.txt   # trae httpx, que usa TestClient
pytest
```

Incluye tests de dominio (RUT, reemplazo, modelos, historial, rutas) y de
integración de la API web completa (`tests/test_web_app.py`, con
`fastapi.testclient.TestClient`), aislados del `salida/`/`historial/` reales
mediante `tmp_path`.

## Estado

- [x] Modelo de datos con validación de RUT
- [x] Motor de fusión plantilla + datos
- [x] Exportación a PDF
- [x] Interfaz de línea de comandos
- [x] Tests (dominio + integración de la API web)
- [x] Interfaz web con formulario (elegir tipo → completar datos → descargar)
- [x] 4 plantillas oficiales (Impact/TechTool × interno/externo)
- [x] Historial de contratos generados, con búsqueda
- [x] Ejecutable de escritorio (PyInstaller)
- [ ] Despliegue
