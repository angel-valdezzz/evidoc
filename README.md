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
