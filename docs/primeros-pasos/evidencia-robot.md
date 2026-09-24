# Quick Start: evidencia de Robot a PDF y Word

Instala EviDoc en el mismo entorno de Python donde ejecutas Robot. Para capturas del navegador instala también SeleniumLibrary; para escritorio debe haber una sesión gráfica activa. El listener y las keywords son independientes: carga ambos.

Si tu proyecto de pruebas usa Poetry, ejecuta desde **ese proyecto** (no desde el repositorio de EviDoc):

```bash
poetry add "git+https://github.com/angel-valdezzz/evidoc.git#feature/legacy-evidence-reporting"
poetry add robotframework-seleniumlibrary
poetry run python -c "import evidoc.robot, evidoc.listener; print(evidoc.robot.__file__)"
```

Si ya clonaste la rama junto al proyecto de pruebas, puedes usar `poetry add --editable ../evidoc` en vez de la dependencia Git. La ruta que imprime el diagnóstico debe apuntar a la versión recién instalada; `evidoc.toml` configura la ejecución, pero no instala la biblioteca. Usa siempre `poetry run robot` y `poetry run evidoc` para que ambos comandos compartan el entorno. En VS Code, selecciona también el intérprete de ese entorno; consúltalo con `poetry env info --path`.

Si al importar el listener aparece `FileNotFoundError` buscando `site-packages/schemas/config.schema.json` o `result.schema.json`, tienes instalada una revisión anterior de la rama. Actualiza la dependencia Git desde el proyecto de pruebas con `poetry update evidoc`. Después confirma que la importación funciona con `poetry run python -c "import evidoc.listener; from evidoc.schema_paths import config_schema_path, result_schema_path; print(config_schema_path().is_file(), result_schema_path().is_file())"`: debe imprimir `True True`.

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    evidoc.robot

*** Test Cases ***
Solicitud del titular
    Open Browser    https://example.org    chrome
    Capture Page Evidence    Credenciales ingresadas    INFO
    Capture Element Evidence    //div[@id="PanelTitular"]    Panel Titular    INFO    include_page=True
    Set Defect    BUG-123
    Capture Desktop Evidence    Evidencia completa    INFO
    Close Browser
```

Sustituye la URL y el locator del ejemplo por los de tu aplicación. Las capturas de página usan el viewport del navegador activo en SeleniumLibrary; las de elemento usan su locator (incluidos prefijos como `css:` o `xpath:`); las de escritorio usan la pantalla completa del sistema y pueden incluir barra de direcciones, fecha y otras ventanas. Para un elemento, `include_page=True` añade primero la captura de contexto y luego la del elemento; si solo quieres el recorte, omite el argumento. Las imágenes pequeñas se amplían hasta el ancho o alto disponible sin deformarlas. `orientation=horizontal` o `orientation=vertical` ajusta el espacio reservado para la imagen. La captura de escritorio puede fallar sin sesión gráfica (por ejemplo, un agente CI sin display); EviDoc registra una advertencia sin fallar el caso.

El resumen del informe conserva la tabla azul del reporte anterior: Aplicación, Requerimiento, Caso de Prueba, Estatus, Duración y la nueva fila roja **Defecto**. `Set Defect` la rellena para el caso actual; de lo contrario queda vacía. Marca, proyecto, fecha y ambiente aparecen en el encabezado o pie del reporte.

## Keywords en un archivo `.resource`

El archivo `resources/evidencia.resource` puede importar las bibliotecas y ofrecer keywords propias de tu proyecto:

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    evidoc.robot

*** Keywords ***
Registrar página
    [Arguments]    ${titulo}
    Capture Page Evidence    ${titulo}    INFO

Registrar panel titular
    Capture Element Evidence    //div[@id="PanelTitular"]    Panel Titular    INFO    orientation=horizontal    include_page=True

Registrar escritorio
    Capture Desktop Evidence    Evidencia completa    INFO
```

En `tests/titular.robot` importa ese recurso y utiliza sus keywords:

```robotframework
*** Settings ***
Resource    ../resources/evidencia.resource

*** Test Cases ***
Validar titular
    Open Browser    https://example.org    chrome
    Registrar página    Vista general del titular
    Registrar panel titular
    Registrar escritorio
    Close Browser
```

`Library    evidoc.robot` importa las keywords. `--listener evidoc.listener` abre y guarda el resultado por cada caso; pásalo al ejecutar Robot, no lo declares como `Library` en el `.resource`. Abre el navegador antes de capturar página o elemento. `Capture Desktop Evidence` se puede usar en este mismo recurso aunque no haya navegador.

## Listener y directorios

```bash
poetry run robot --outputdir output --listener evidoc.listener tests/
poetry run evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

El listener toma `${OUTPUT DIR}` de Robot. Por defecto escribe `output/evidoc/metadata/run-<id>/test-<id>/result.json`; con almacenamiento `file`, la misma carpeta contiene `artifacts/*.png`. Los informes se generan en `output/evidoc/reports` al ejecutar `build`. Robot continúa escribiendo `output.xml`, `log.html` y `report.html` directamente en `output`.

La configuración opcional del listener usa los argumentos posicionales de Robot, en este orden: `root_dir`, `storage`, `application`, `requirement`. Para cambiar storage y mantener el directorio por defecto, indica explícitamente el directorio:

```bash
robot --outputdir output --listener evidoc.listener.Listener:output/evidoc/metadata:base64:VisualTime:REQ-123 tests/
```

En Windows, Robot separa argumentos de listener con `:`; si la ruta incluye letra de unidad, usa una ruta relativa o una instancia Python del listener. Para Pabot, usa **el mismo directorio de metadata absoluto o relativo al cwd** en todos los workers y construye los reportes tras terminar todos los procesos:

```bash
pabot --outputdir output --listener evidoc.listener.Listener:output/evidoc/metadata:file tests/
evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

Cada caso tiene un ID único. El ID de ejecución se crea atómicamente y se comparte por los workers que apuntan al mismo directorio. Usa un directorio nuevo por ejecución para no mezclar resultados anteriores.

## Python sin subprocess

```python
from robot import run
from evidoc import build

code = run("tests", outputdir="output", listener="evidoc.listener")
reports = build(
    input_dir="output/evidoc/metadata",
    output_dir="output/evidoc/reports",
    formats=["pdf", "docx"],
)
print(code, reports)
```

`build()` retorna una lista de `Path`. El modo por defecto genera un documento por caso y formato seleccionado; `mode="run"` genera uno combinado por formato. Sin lista explícita y sin configuración, el formato predeterminado es PDF. `evidoc generate` permanece disponible para los flujos anteriores.

## `evidoc.toml`

EviDoc ya soportaba `evidoc.toml` para `generate`. Ahora `build()` y el listener también lo autodetectan en el directorio desde el que ejecutas Robot/Python:

```toml
metadata_dir = "output/evidoc/metadata"
output_dir = "output/evidoc/reports"
application = "D-SAAS-283 Plataforma Operativa De Salud"
project = "Espartaco"
environment = "QA"
brand = "AXA"
formats = ["pdf", "docx"]
storage = "base64"  # o "file"
mode = "single"
```

En este caso bastan `robot --outputdir output --listener evidoc.listener tests/` y `evidoc build`. Un argumento explícito de listener, CLI o `build()` prevalece sobre el TOML. También acepta `aplicacion`, `proyecto` y `ambiente` como aliases de las claves en inglés; no declares las dos versiones de una clave. `source_dir` y `format` antiguos siguen siendo válidos para `evidoc generate`. `metadata_dir` indica la ruta compartida para el listener y `build`, incluso con Pabot. Puedes pasar `config_path="ruta/evidoc.toml"` a `build()` o `--config ruta/evidoc.toml` al CLI.

El archivo se llama `evidoc.toml` y se busca en el directorio desde el que lanzas los comandos. También se admite `evidoc.json` con las mismas claves, por ejemplo `{"metadata_dir":"output/evidoc/metadata","output_dir":"output/evidoc/reports","formats":["pdf","docx"],"storage":"file"}`. Si existen los dos, se elige TOML. `pyproject.toml` gestiona la instalación de Poetry; `evidoc.toml` o `evidoc.json` configura EviDoc. El JSON de ejemplo del propio repositorio conserva claves del CLI antiguo (`source_dir` y `format`): para este flujo utiliza `metadata_dir` y `formats`.

## Almacenamiento y metadatos

`file` guarda PNG independientes y su ruta relativa en `result.json`. `base64` incrusta los bytes de cada PNG en `data` y evita crear PNG separados. Los adjuntos no fotográficos siguen siendo archivos. Ambos formatos de reporte usan el mismo modelo de resultado y aceptan ambas estrategias. PDF es el documento de entrega; DOCX conserva tablas, textos e imágenes editables en Word.

Los artefactos de imagen registran `capture` (`page`, `element` o `desktop`) y `orientation`. Los pasos y sus referencias a artefactos conservan el orden en que se invocaron las keywords. Las APIs anteriores `Capture Screenshot`, `Log Step`, `Log Info`, `Attach Artifact` y `evidoc generate` siguen disponibles.
