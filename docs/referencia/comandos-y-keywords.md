# Comandos y keywords

## CLI

```bash
poetry run evidoc build --input-dir PATH --output-dir PATH --formats pdf,docx [--exclude-status FAIL,SKIP]
poetry run evidoc merge --input-dir RUN --input-dir RERUN --output-dir FINAL
poetry run evidoc generate [--source_dir PATH] [--output_dir PATH] [--mode run|single] [--format pdf|docx]
poetry run evidoc tui
poetry run evidoc docs manual
poetry run evidoc docs robot-library
poetry run ruff check .
poetry run ruff format .
poetry run mypy evidoc tests scripts
poetry run lint-imports
```

`evidoc docs manual` abre el manual offline generado con MkDocs y empaquetado dentro del `wheel` instalado localmente.

`evidoc docs robot-library` abre la referencia HTML de la libreria `evidoc.robot` generada con `libdoc` y empaquetada dentro de la distribucion instalada.

### Corrida completa de calidad

```bash
poetry run ruff check . && poetry run mypy evidoc tests scripts && poetry run lint-imports && poetry run pytest tests/unit -m unit && poetry run pytest tests/acceptance -m acceptance
```

## Python API

```python
api.configure_context(root_dir="./results")
api.start_test("Nombre de prueba")
api.log_step("Paso", "PASS")
api.log_info("Mensaje")
api.capture_screenshot(driver, title="Pantalla")
api.attach_file("./archivo.txt", "Descripcion")
api.reference_file("./descarga.pdf", "Archivo para subir, sin copia")
api.end_test("PASS", 3.2)
```

## Robot Framework

```robotframework
*** Settings ***
Library    evidoc.robot

*** Test Cases ***
Registrar Evidencia Minima
    Log Step    Paso visible    PASS
    Log Info    Mensaje tecnico
    Log Warning    Riesgo detectado
    Log Error    Fallo observado
    Attach Artifact    ${CURDIR}${/}archivo.txt    Archivo de soporte
    Attach File    ${RUTA_FINAL}    description=Carátula descargada
    Capture Page Evidence    Vista del titular    INFO    description=Folio visible
    Capture Screenshot    driver=${driver}    title=Pantalla final
```

La referencia completa de argumentos, descripcion funcional y notas de uso para cada keyword se consulta desde el HTML abierto con `evidoc docs robot-library`.
