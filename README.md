# Evidoc

Evidoc almacena evidencia de pruebas estructurada en disco y después genera reportes en PDF o DOCX.

## Instalacion

```bash
poetry install
```

## Manual de usuario

Haz el build local del manual tecnico para usuarios finales:

```bash
poetry install --with docs
poetry run mkdocs build
poetry run evidoc docs manual
```

`evidoc docs manual` abre el sitio offline de MkDocs incluido en el paquete instalado. El sitio estatico se almacena en `evidoc/resources/docs/site` para poder distribuirlo dentro del `wheel` generado.

## Tests

La suite de tests se divide en dos capas:

- Unit tests en `tests/unit` para reglas de dominio, servicios de runtime y la capa de API agnostica al framework.
- Acceptance tests en `tests/acceptance` usando escenarios estilo Gherkin/Cucumber ejecutados con `pytest-bdd`.

Instala las dependencias de testing:

```bash
poetry install --with test,acceptance
```

Ejecuta la suite unitaria:

```bash
poetry run pytest tests/unit -m unit
```

Ejecuta la suite de acceptance:

```bash
poetry run pytest tests/acceptance -m acceptance
```

Ejecuta todo con coverage:

```bash
poetry run pytest --cov=evidoc
```

## Calidad de codigo

El proyecto ahora incluye un stack de analisis estatico para calidad y arquitectura:

- `ruff` para lint, formato y ordenamiento de imports.
- `mypy` para chequeo de tipos.
- `import-linter` para validar reglas de dependencia entre capas.

Instala el entorno completo de calidad:

```bash
poetry install --with dev,test,acceptance,docs
```

Comandos principales:

```bash
poetry run ruff check .
poetry run ruff format .
poetry run mypy evidoc tests scripts
poetry run lint-imports
```

Ejecuta todo lo relacionado con calidad en una sola corrida:

```bash
poetry run ruff check . && poetry run mypy evidoc tests scripts && poetry run lint-imports && poetry run pytest tests/unit -m unit && poetry run pytest tests/acceptance -m acceptance
```

## VS Code

El repositorio incluye configuracion lista para trabajar desde VS Code:

- formato al guardar con Ruff
- autofix y organize imports al guardar
- diagnosticos de `mypy`
- tareas para `ruff`, `mypy`, `import-linter` y un agregado `Quality: all`
- compatibilidad con `Error Lens` para mostrar errores inline

Archivos relevantes:

- `.vscode/settings.json`
- `.vscode/tasks.json`
- `.vscode/extensions.json`
- `scripts/vscode_import_lint.py`

Para ver tambien violaciones de arquitectura dentro de VS Code y `Error Lens`, ejecuta la tarea `Import Linter: VSCode diagnostics`. `import-linter` sigue siendo la validacion oficial de arquitectura, y ese script adicional existe solo para traducir esas reglas a diagnosticos por archivo y linea dentro del editor.

## Generar reportes

```bash
poetry run evidoc generate --source_dir ./results --output_dir ./reports --mode run --format pdf
poetry run evidoc generate --source_dir ./results --output_dir ./reports --mode single --format docx
```

## Robot Framework

```bash
robot --listener evidoc.listener --pythonpath . path/to/tests.robot
```

Import the keyword library from Robot:
Importa la libreria de keywords desde Robot:

```robot
*** Settings ***
Library    evidoc.robot
```

Ejemplo minimo:

```robot
*** Settings ***
Library    evidoc.robot

*** Test Cases ***
Capture Evidence
    Log Step    Open checkout    PASS
    Log Info    Navigated to checkout
    Attach Artifact    ${CURDIR}${/}sample.txt    Input data
```

Un ejemplo ejecutable end-to-end con un driver demo para screenshots se encuentra en `examples/robot/evidoc_example.robot`.
