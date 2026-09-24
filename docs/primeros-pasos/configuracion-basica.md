# Configuración básica

EviDoc busca `evidoc.toml` o `evidoc.json` en el directorio donde ejecutas Robot y `build`. Puedes indicar otro archivo con `--config` o pasar rutas en la CLI.

```toml
metadata_dir = "output/run/robot/evidoc/metadata"
output_dir = "output/run/robot/evidoc/reports"
formats = ["pdf", "docx"]
mode = "single"
storage = "file"
application = "Portal QA"
```

El listener escribe en `metadata_dir` y `build` lee esa carpeta. Si omites `metadata_dir`, el listener usa `${OUTPUT DIR}/evidoc/metadata`. `output_dir` recibe los PDF/DOCX y `upload-manifest.json`.

| Campo | Uso |
| --- | --- |
| `metadata_dir` | Carpeta que comparten listener y `build`. |
| `output_dir` | Carpeta de reportes y manifiesto. |
| `formats` | Lista de formatos: `pdf`, `docx`. |
| `mode` | `single`: un documento por caso; `run`: uno por corrida. |
| `storage` | `file`: PNG por separado; `base64`: imagen en JSON. |
| `exclude_status` | Estado o lista de estados omitidos al construir reportes y manifiesto. |
| `application`, `requirement`, `project`, `environment`, `brand` | Datos guardados en cada resultado. |

También se aceptan `source_dir` y `format` para configuraciones anteriores. Los argumentos explícitos de `build` tienen prioridad sobre el archivo de configuración. El filtro, si lo necesitas, puede escribirse así:

```toml
exclude_status = ["FAIL", "SKIP"]
```

Para dos tandas de pruebas, utiliza `merge` y pasa su carpeta de salida como `--input-dir` de `build`. Consulta [Run y rerun](../guias/cli.md).
