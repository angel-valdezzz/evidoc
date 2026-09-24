# API Python

## Construir reportes

```python
from evidoc import build

reports = build(
    input_dir="output/evidoc/metadata",
    output_dir="output/evidoc/reports",
    formats=["pdf", "docx"],
    exclude_status=["FAIL", "SKIP"],
    defects=["TC036=BUG-123"],
)
```

`build()` devuelve una lista de rutas `Path` y crea `upload-manifest.json` en `output_dir`. `exclude_status` acepta un estado (`"FAIL"`) o una lista; el filtro afecta tanto a los documentos como al manifiesto. `defects` acepta claves repetidas con las mismas reglas que `--defect`: sin nombre solo si queda un caso seleccionado; con varios casos, `Nombre del caso=BUG-123`.

## Combinar resultados (opcional)

```python
from evidoc import build, merge

index = merge(
    ["output/primera/metadata", "output/segunda/metadata"],
    "output/final/metadata",
)
reports = build(input_dir=index.parent, output_dir="output/final/reports")
```

`merge()` devuelve la ruta de `merged-results.json`. Selecciona el último resultado completo para cada caso y mantiene referencias a los archivos de las ejecuciones originales. Con una ejecución, usa `build()` directamente.

## Captura desde Python

```python
from evidoc.api import EvidocAPI

api = EvidocAPI(root_dir="output/evidoc/metadata")
api.start_test("TC036", full_name="Solicitud.TC036")
api.capture_image(png_bytes, title="Solicitud registrada", description="Folio visible")
api.attach_file("output/descargas/caratula.pdf", "Carátula de la póliza")
api.end_test("PASS", 12.5)
```

`capture_image` recibe bytes PNG. `attach_file` registra la ruta absoluta de un archivo existente para el manifiesto, sin copiarlo. `full_name` permite identificar el mismo caso entre ejecuciones; el listener de Robot Framework lo obtiene automáticamente. Los defectos se proporcionan después, al llamar a `build()`.
