# EviDoc

EviDoc registra evidencias de casos de prueba y genera un PDF o DOCX **por caso**. Funciona con Robot Framework y con scripts Python. Las capturas se guardan durante la ejecución; `build` crea los documentos y `upload-manifest.json` después.

## Instalación

En el proyecto de pruebas, coloca el archivo wheel de EviDoc en `assets/` e instálalo en el entorno Poetry (ajusta la versión al nombre recibido):

```bash
poetry add ./assets/evidoc-0.1.0-py3-none-any.whl
poetry run evidoc --help
```

Para capturas del navegador, instala también `robotframework-seleniumlibrary` en ese entorno. El listener y la biblioteca deben ejecutarse con el mismo Poetry.

## Primer reporte con Robot Framework

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    evidoc.robot

*** Test Cases ***
Registrar solicitud
    Open Browser    https://example.test    chrome
    Capture Page Evidence    Solicitud registrada    INFO    description=Se muestra el folio asignado
    Attach File    ${OUTPUT DIR}${/}caratula.pdf    description=Carátula descargada
    Close Browser
```

`Attach File` se usa cuando el archivo ya existe; apunta a su ruta original y lo agrega al manifiesto. No lo copia ni lo incrusta en los documentos.

```bash
poetry run robot --outputdir output --listener evidoc.listener tests/
poetry run evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

La segunda orden produce `Nombre_del_caso.pdf`, `Nombre_del_caso.docx` y `upload-manifest.json`. Si solo necesitas PDF, usa `--formats pdf`. El manifiesto contiene una lista `tests`; cada entrada tiene `name` y `files` con rutas absolutas a documentos y archivos registrados. Con una sola ejecución basta `build`.

## Defectos y selección de casos

Asigna el defecto al construir los documentos, una vez que tengas su clave en Jira:

```bash
# Solo cuando build selecciona un caso:
poetry run evidoc build --input-dir output/evidoc/metadata --defect BUG-123

# Si build selecciona varios casos, especifica el nombre del caso:
poetry run evidoc build --input-dir output/evidoc/metadata --defect 'TC036=BUG-123' --defect 'TC037=BUG-456'
```

Repite `--defect 'TC036=BUG-789'` para asignar dos claves a un mismo caso. El nombre debe coincidir con `${TEST NAME}` de Robot, o con el nombre completo único de la prueba. Un defecto sin nombre se rechaza cuando hay más de un caso seleccionado. `--exclude-status FAIL,SKIP` retira esos casos de los reportes y del manifiesto antes de asignar defectos. Los metadatos originales no cambian.

Si tienes resultados de más de una ejecución y deseas conservar el último resultado por caso, usa `merge` antes de `build`:

```bash
poetry run evidoc merge --input-dir output/primera/metadata --input-dir output/segunda/metadata --output-dir output/final/metadata
poetry run evidoc build --input-dir output/final/metadata --output-dir output/final/reports --exclude-status FAIL,SKIP
```

`merge` es opcional y acepta carpetas de entrada en orden cronológico. Su índice mantiene referencias a los archivos originales: conserva esas carpetas hasta finalizar la generación y la carga.

## API Python y configuración

```python
from evidoc import build, merge

reports = build(
    input_dir="output/evidoc/metadata",
    output_dir="output/evidoc/reports",
    formats=["pdf", "docx"],
    defects=["TC036=BUG-123"],
)
```

`build()` devuelve una lista de rutas `Path`. Puedes fijar los valores habituales en `evidoc.toml`; los argumentos del comando o de Python tienen prioridad:

```toml
metadata_dir = "output/evidoc/metadata"
output_dir = "output/evidoc/reports"
formats = ["pdf", "docx"]
storage = "file"
```

Para consultar la guía instalada sin conexión:

```bash
poetry run evidoc docs manual
poetry run evidoc docs library
```

Consulta el [manual de usuario](docs/index.md) para las keywords, opciones de consola, rutas de salida y ejemplos de Python. Para desarrollar EviDoc en este repositorio: `poetry install --with dev,test,acceptance,docs` y `poetry run pytest`.
