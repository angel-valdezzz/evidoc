# API Python

Puedes ejecutar Robot y construir los reportes en el mismo proceso. No necesitas llamar al CLI desde `subprocess`:

```python
from robot import run
from evidoc import build

code = run("tests", outputdir="output", listener="evidoc.listener")
reports = build(
    input_dir="output/evidoc/metadata",
    output_dir="output/evidoc/reports",
    formats=["pdf", "docx"],
)
print(code, reports)
```

`build()` devuelve rutas `Path` a los PDF/DOCX. También crea `upload-manifest.json` en `output_dir`. Para no crear reportes de ciertos estados, pasa `exclude_status="FAIL"` o `exclude_status=["FAIL", "SKIP"]`. El mismo filtro determina qué casos aparecen en el manifiesto.

## Run y rerun

Cuando hayas ejecutado dos tandas, fusiona su metadata **antes** de construir los reportes:

```python
from evidoc import build, merge

index = merge(
    ["output/run/evidoc/metadata", "output/rerun/evidoc/metadata"],
    "output/final/evidoc/metadata",
)
reports = build(
    input_dir=index.parent,
    output_dir="output/final/evidoc/reports",
    formats=["pdf", "docx"],
    exclude_status=["FAIL", "SKIP"],
)
```

`merge()` devuelve la ruta de `merged-results.json`. Si el mismo caso se ejecutó dos veces, conserva el intento completo de la última carpeta. Los archivos originales permanecen en sus directorios; no se copian durante la fusión. Con una sola ejecución, llama directamente a `build()`.

## Capturas y archivos desde Python

La API de captura acepta bytes PNG sin depender de Selenium:

```python
from evidoc.api import EvidocAPI

api = EvidocAPI(root_dir="output/evidoc/metadata")
api.start_test("TC036", full_name="Solicitud.TC036")
api.capture_image(png_bytes, title="Solicitud registrada", description="Folio visible")
api.reference_file("output/descargas/caratula.pdf", "Carátula de la póliza")
api.end_test("PASS", 12.5)
```

`reference_file` guarda la ruta absoluta para el manifiesto sin copiar el archivo. `attach_file` y `attach_artifact` conservan la API previa que copia el archivo a metadata. `start_test(full_name=...)` permite identificar el mismo caso entre ejecuciones; en Robot el listener proporciona ese dato automáticamente.
