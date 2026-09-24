# EviDoc

EviDoc registra evidencias de pruebas automatizadas y crea un PDF o DOCX por caso. Funciona con Robot Framework, Pabot o un pipeline Python. Las capturas y los resultados se guardan durante la ejecución; los reportes se construyen después.

## Instalación en tu proyecto de pruebas

```bash
poetry add "git+https://github.com/angel-valdezzz/evidoc.git#feature/legacy-evidence-reporting"
poetry add robotframework-seleniumlibrary
poetry run python -c "import evidoc.robot, evidoc.listener; print(evidoc.robot.__file__)"
```

Usa siempre `poetry run robot` y `poetry run evidoc` desde el mismo proyecto para que compartan el entorno. SeleniumLibrary solo es necesaria para capturas de página o elemento; `Capture Desktop Evidence` no depende del navegador.

## Primer reporte con Robot

En `resources/evidencia.resource`:

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    evidoc.robot

*** Keywords ***
Registrar solicitud
    Capture Page Evidence    Solicitud registrada    INFO    description=Se muestra el folio asignado
    Capture Element Evidence    css:#PanelTitular    Panel titular    INFO    description=Datos del titular
```

En la suite importa `Resource    ../resources/evidencia.resource`, abre el navegador y llama `Registrar solicitud`. Activa el listener **en el comando**, no en el recurso:

```bash
poetry run robot --outputdir output --listener evidoc.listener tests/
poetry run evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

Los reportes y `upload-manifest.json` quedan en `output/evidoc/reports`. El manifiesto agrupa las rutas absolutas por caso para una herramienta externa de carga. Sin `--exclude-status`, `build` incluye todos los estados.

## Archivos descargados

Registra la **ruta final** una vez que el archivo esté descargado y renombrado:

```robotframework
Attach File    ${RUTA_CARATULA}    description=Carátula de la póliza
```

`Attach File` no copia el archivo ni lo introduce en PDF/DOCX. EviDoc verifica que siga existiendo al construir el manifiesto. `Attach Artifact` conserva su comportamiento anterior de copiar un archivo a metadata; úsalo solo si necesitas esa copia.

## Run y rerun

Si reejecutas los casos fallidos, conserva las dos carpetas de metadata y fusiona los resultados antes de construir los reportes:

```bash
poetry run evidoc merge --input-dir output/run/evidoc/metadata --input-dir output/rerun/evidoc/metadata --output-dir output/final/evidoc/metadata
poetry run evidoc build --input-dir output/final/evidoc/metadata --output-dir output/final/evidoc/reports --formats pdf,docx --exclude-status FAIL,SKIP
```

`merge` toma el último intento completo de cada caso. No copia capturas: la metadata final apunta a las carpetas originales, que deben permanecer disponibles. `build` filtra **después** de fusionar. Si ejecutas Robot una sola vez, omite `merge` y usa `build` directamente sobre su metadata.

Con Pabot, pasa a todos los workers el mismo directorio de metadata:

```bash
poetry run pabot --outputdir output/run/robot --listener evidoc.listener.Listener:output/run/evidoc/metadata:file tests/
```

## Pipeline Python

```python
from robot import run
from evidoc import build, merge

run("tests", outputdir="output/run/robot", listener="evidoc.listener")
# Si hubo rerun, usa primero merge([metadata_run, metadata_rerun], metadata_final).
reports = build(
    input_dir="output/run/robot/evidoc/metadata",
    output_dir="output/run/reports",
    formats=["pdf", "docx"],
    exclude_status=["FAIL", "SKIP"],
)
```

`build()` devuelve una lista de rutas `Path` a los reportes. Tanto CLI como API usan el mismo caso de uso. `exclude_status` admite un estado (`"FAIL"`) o una lista. `evidoc generate` sigue disponible para los flujos anteriores.

## Configuración opcional

EviDoc lee `evidoc.toml` (o `evidoc.json`) desde el directorio donde ejecutas el comando. Los argumentos explícitos prevalecen:

```toml
metadata_dir = "output/evidoc/metadata"
output_dir = "output/evidoc/reports"
application = "VisualTime"
project = "Espartaco"
environment = "QA"
formats = ["pdf", "docx"]
storage = "file"  # o "base64" para imágenes embebidas en result.json
mode = "single"
exclude_status = ["FAIL", "SKIP"]
```

Las capturas de página y elemento usan SeleniumLibrary. Las de escritorio usan una sesión gráfica activa. EviDoc muestra como máximo dos capturas por página, con la descripción debajo de cada imagen.

## Manual y desarrollo

Consulta el [Quick Start detallado](docs/primeros-pasos/evidencia-robot.md) y el [manual](docs/index.md). Para abrir la versión offline incluida en el paquete, usa `poetry run evidoc docs manual`.

```bash
poetry install --with dev,test,acceptance,docs
poetry run pytest
poetry run ruff check .
poetry run ruff format --check .
poetry run mypy evidoc tests scripts
poetry run lint-imports
poetry run mkdocs build
```
