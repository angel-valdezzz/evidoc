# Python API

## Cuando usarla

La API es la opcion correcta si quieres integrar Evidoc dentro de una automatizacion Python o dentro de una herramienta interna.

## Ciclo minimo

```python
from evidoc import api

api.configure_context(root_dir="./results")
api.start_test("Checkout happy path")
api.log_step("Open checkout", "PASS")
api.log_info("Checkout page loaded")
api.attach_file("./examples/sample_attachment.txt", "Datos usados en la prueba")
api.end_test("PASS", 2.84)
```

## Operaciones disponibles

| Operacion | Efecto |
| --- | --- |
| `configure_context(...)` | Define `root_dir` y esquema |
| `start_test(name)` | Abre contexto de prueba |
| `log_step(title, status)` | Registra un paso |
| `log_info`, `log_warning`, `log_error` | Agrega logs al paso actual |
| `capture_screenshot(driver, ...)` | Captura imagen desde un driver compatible |
| `attach_file(path, description)` | Adjunta un archivo existente |
| `end_test(status, duration)` | Cierra y persiste la prueba |
| `clear_context()` | Limpia el contexto actual |

## Ejemplo con screenshots

```python
from pathlib import Path
from evidoc import api

class DemoDriver:
    def screenshot(self, path: str) -> bool:
        Path(path).write_bytes(b"png")
        return True

api.configure_context(root_dir="./results")
api.start_test("Login valid user")
api.log_step("Open login page", "PASS")
api.capture_screenshot(DemoDriver(), title="Login page", description="Estado inicial")
api.log_info("Form rendered correctly")
api.end_test("PASS", 1.12)
```

!!! warning "Regla de contexto"
    Si llamas `log_step`, `log_info` o `capture_screenshot` sin una prueba activa, Evidoc no rompe la ejecucion, pero emitira advertencias y no persistira esa evidencia de la forma esperada.
