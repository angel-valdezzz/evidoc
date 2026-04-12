# Comandos y keywords

## CLI

```bash
poetry run evidoc generate [--source_dir PATH] [--output_dir PATH] [--mode run|single] [--format pdf|docx]
poetry run evidoc tui
poetry run evidoc docs manual
poetry run evidoc docs robot-library
```

`evidoc docs manual` abre el manual offline generado con MkDocs y empaquetado dentro del `wheel` instalado localmente.

`evidoc docs robot-library` abre la referencia HTML de la libreria `evidoc.robot` generada con `libdoc` y empaquetada dentro de la distribucion instalada.

## Python API

```python
api.configure_context(root_dir="./results")
api.start_test("Nombre de prueba")
api.log_step("Paso", "PASS")
api.log_info("Mensaje")
api.capture_screenshot(driver, title="Pantalla")
api.attach_file("./archivo.txt", "Descripcion")
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
    Capture Screenshot    driver=${driver}    title=Pantalla final
```

La referencia completa de argumentos, descripcion funcional y notas de uso para cada keyword se consulta desde el HTML abierto con `evidoc docs robot-library`.
