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
    Capture Page Evidence    Credenciales ingresadas    INFO    description=Formulario listo
    Capture Element Evidence    //div[@id="PanelTitular"]    Panel Titular    INFO    include_page=True    description=Datos del titular
    Set Defect    BUG-123
    Capture Desktop Evidence    Evidencia completa    INFO
    Close Browser
```

Sustituye la URL y el locator por los de tu aplicación. La captura de página muestra el área visible del navegador; la de elemento usa un locator de SeleniumLibrary; la de escritorio muestra la pantalla completa. `description=` aparece debajo de la imagen. `include_page=True` agrega una vista general antes del recorte del elemento. `orientation=horizontal` o `vertical` ajusta el espacio de la imagen. Sin una sesión gráfica, la captura de escritorio registra una advertencia.

El resumen del informe conserva la tabla azul del reporte anterior: Aplicación, Requerimiento, Caso de Prueba, Estatus, Duración y la nueva fila roja **Defecto**. `Set Defect` la rellena para el caso actual; de lo contrario queda vacía. Marca, proyecto, fecha y ambiente aparecen en el encabezado o pie del reporte.

## Keywords en un archivo `.resource`

El archivo `resources/evidencia.resource` puede importar las bibliotecas y ofrecer keywords propias de tu proyecto:

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    evidoc.robot

*** Keywords ***
Registrar página
    [Arguments]    ${titulo}    ${descripcion}=${EMPTY}
    Capture Page Evidence    ${titulo}    INFO    description=${descripcion}

Registrar panel titular
    Capture Element Evidence    //div[@id="PanelTitular"]    Panel Titular    INFO    orientation=horizontal    include_page=True    description=Datos verificados

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

El listener toma `${OUTPUT DIR}` de Robot. Por defecto escribe `output/evidoc/metadata/run-<id>/test-<id>/result.json`; con almacenamiento `file`, la misma carpeta contiene `artifacts/*.png`. `build` genera los reportes y `upload-manifest.json` en `output/evidoc/reports`. Robot continúa escribiendo `output.xml`, `log.html` y `report.html` directamente en `output`.

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

## Archivos descargados y manifiesto

Si el caso descarga una carátula o cotización, espera a que termine la descarga, renombra el archivo y registra su ruta final:

```robotframework
Attach File    ${RUTA_CARATULA}    description=Carátula de la póliza
```

EviDoc **no copia** el archivo ni lo introduce en el reporte. La ruta absoluta aparece junto a las rutas PDF/DOCX del caso en `upload-manifest.json`:

```json
{
  "tests": [
    {
      "name": "TC036",
      "files": ["C:\\output\\reports\\TC036.pdf", "C:\\output\\descargas\\caratula.pdf"]
    }
  ]
}
```

El archivo debe permanecer en esa ruta hasta que lo consuma tu herramienta de carga. Si desaparece antes de `build`, EviDoc detiene la construcción con un error que identifica el caso y la ruta. `Attach Artifact` conserva su función anterior de copiar archivos a metadata.

## Run y rerun sin reportes duplicados

Si el rerun solo ejecuta los fallidos, crea metadata separada para ambas tandas. Fusiona primero; el segundo directorio reemplaza los casos repetidos, incluso si volvieron a fallar:

```bash
poetry run evidoc merge --input-dir output/run/evidoc/metadata --input-dir output/rerun/evidoc/metadata --output-dir output/final/evidoc/metadata
poetry run evidoc build --input-dir output/final/evidoc/metadata --output-dir output/final/evidoc/reports --formats pdf,docx --exclude-status FAIL,SKIP
```

`merge` crea un índice de rutas y no duplica capturas. Conserva las carpetas originales. `build` excluye los estados indicados **después** de elegir el último intento y solo esos casos aparecen en el manifiesto. Una ejecución sencilla usa `build` directamente, sin `merge`. Un único estado también funciona: `--exclude-status FAIL`.

## Python sin subprocess

```python
from robot import run
from evidoc import build, merge

code = run("tests", outputdir="output", listener="evidoc.listener")
reports = build(
    input_dir="output/evidoc/metadata",
    output_dir="output/evidoc/reports",
    formats=["pdf", "docx"],
)
print(code, reports)
```

`build()` retorna una lista de `Path` a los reportes; también escribe el manifiesto. Para fusionar, `merge([metadata_run, metadata_rerun], metadata_final)` retorna la ruta de `merged-results.json`. Sin `mode` en la configuración, se genera un documento por caso; `mode="run"` crea uno combinado. El nombre individual es el nombre seguro del caso, sin ID adicional. Si dos casos producirían el mismo archivo, `build` avisa para no sobrescribirlo. `evidoc generate` permanece disponible para flujos anteriores.

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
exclude_status = ["FAIL", "SKIP"]  # opcional
```

En este caso bastan `robot --outputdir output --listener evidoc.listener tests/` y `evidoc build`. Un argumento explícito de listener, CLI o `build()` prevalece sobre el TOML. También acepta `aplicacion`, `proyecto` y `ambiente` como aliases de las claves en inglés; no declares las dos versiones de una clave. `source_dir` y `format` antiguos siguen siendo válidos para `evidoc generate`. `metadata_dir` indica la ruta compartida para el listener y `build`, incluso con Pabot. Puedes pasar `config_path="ruta/evidoc.toml"` a `build()` o `--config ruta/evidoc.toml` al CLI.

El archivo se llama `evidoc.toml` y se busca en el directorio desde el que lanzas los comandos. También se admite `evidoc.json` con las mismas claves, por ejemplo `{"metadata_dir":"output/evidoc/metadata","output_dir":"output/evidoc/reports","formats":["pdf","docx"],"storage":"file"}`. Si existen los dos, se elige TOML. `pyproject.toml` gestiona la instalación de Poetry; `evidoc.toml` o `evidoc.json` configura EviDoc. El JSON de ejemplo del propio repositorio conserva claves del CLI antiguo (`source_dir` y `format`): para este flujo utiliza `metadata_dir` y `formats`.

## Almacenamiento y metadatos

`file` guarda PNG independientes y su ruta relativa en `result.json`. `base64` incrusta los bytes del PNG en `data`. Estas opciones afectan a las **capturas**; `Attach File` conserva una referencia a un archivo externo, sin copiarlo. PDF es el documento de entrega; DOCX permite editar el texto posteriormente.

Los artefactos de imagen registran `capture` (`page`, `element` o `desktop`) y `orientation`. Los pasos y sus referencias a artefactos conservan el orden en que se invocaron las keywords. Las APIs anteriores `Capture Screenshot`, `Log Step`, `Log Info`, `Attach Artifact` y `evidoc generate` siguen disponibles.

En PDF y DOCX, el color de los diamantes indica el estado del paso. Cada página tiene como máximo dos capturas y la descripción aparece debajo de la imagen.
