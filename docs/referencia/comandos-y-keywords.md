# Comandos y keywords

## Consola

```bash
poetry run evidoc build --input-dir PATH --output-dir PATH --formats pdf,docx
poetry run evidoc build --input-dir PATH --exclude-status FAIL,SKIP --defect 'TC036=BUG-123'
poetry run evidoc merge --input-dir PATH_A --input-dir PATH_B --output-dir PATH_FINAL
poetry run evidoc docs manual
poetry run evidoc docs library
poetry run evidoc tui
```

Consulta la [guía de comandos](../guias/cli.md) para todas las opciones, ejemplos y reglas de asignación de defectos. `build` funciona sin `merge` con una sola ejecución.

## Robot Framework

```robotframework
*** Settings ***
Library    evidoc.robot

*** Test Cases ***
Validar solicitud
    Capture Page Evidence    Solicitud abierta    INFO    description=Formulario visible
    Log Step    Validar resultado    PASS
    Attach File    ${OUTPUT DIR}${/}solicitud.pdf    description=Documento generado
```

Las keywords disponibles y sus argumentos están en la [guía de Robot Framework](../guias/robot-framework.md). `poetry run evidoc docs library` abre la referencia completa incluida en el paquete.

## Python

```python
from evidoc import build, merge
from evidoc.api import EvidocAPI

api = EvidocAPI(root_dir="output/evidoc/metadata")
api.start_test("TC036")
api.attach_file("output/descargas/solicitud.pdf", "Solicitud")
api.end_test("PASS", 5.0)
reports = build(input_dir="output/evidoc/metadata", defects=["BUG-123"])
```

[Guía de la API](../guias/python-api.md) · [Archivos de salida](../guias/reportes-y-salidas.md)
