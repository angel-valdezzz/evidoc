# Configuración básica

Puedes guardar las rutas y formatos habituales en `evidoc.toml` en el directorio desde el que ejecutas las pruebas:

```toml
metadata_dir = "output/evidoc/metadata"
output_dir = "output/evidoc/reports"
formats = ["pdf", "docx"]
storage = "file"
application = "Portal de pruebas"
project = "Proyecto QA"
environment = "QA"
exclude_status = ["SKIP"]
```

| Clave | Función |
| --- | --- |
| `metadata_dir` | Carpeta que comparten el listener y `build`. |
| `output_dir` | Destino de PDF, DOCX y manifiesto. |
| `formats` | Formatos que se generan al usar `build`. |
| `storage` | `file` guarda capturas en disco; `base64` las incluye en el JSON del resultado. |
| `application`, `project`, `environment` | Información del encabezado del reporte. |
| `exclude_status` | Estados omitidos de los documentos y del manifiesto. |

También se admite `evidoc.json`. Un argumento explícito de consola o de Python prevalece sobre el archivo. Para elegir un archivo concreto, usa `--config ruta/evidoc.toml` o `build(config_path="ruta/evidoc.toml")`. El defecto se asigna al construir el reporte con `--defect` o `defects`; no se define durante la ejecución.
