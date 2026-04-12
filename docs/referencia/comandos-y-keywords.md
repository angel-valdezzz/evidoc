# Comandos y keywords

## CLI

```bash
poetry run evidoc generate [--source_dir PATH] [--output_dir PATH] [--mode run|single] [--format pdf|docx]
poetry run evidoc tui
```

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
