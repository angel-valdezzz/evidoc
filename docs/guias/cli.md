# Comandos de consola

Ejecuta `poetry run evidoc --help` en el entorno Poetry donde instalaste EviDoc.

## `build`: documentos y manifiesto

```bash
poetry run evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

| Opción | Uso |
| --- | --- |
| `--input-dir PATH` | Directorio de resultados (`result.json`) o índice de `merge`. |
| `--output-dir PATH` | Directorio de documentos y `upload-manifest.json`. |
| `--formats pdf,docx` | Formatos; acepta uno o ambos. |
| `--exclude-status FAIL,SKIP` | Excluye los estados indicados de documentos y manifiesto. |
| `--defect BUG-123` | Asigna un defecto cuando se selecciona exactamente un caso. Se puede repetir. |
| `--defect 'Nombre del caso=BUG-123'` | Asigna el defecto a ese caso. Obligatorio si se seleccionan varios casos. Se puede repetir. |
| `--config PATH` | Usa un archivo `evidoc.toml` o `evidoc.json` específico. |

`--defect` acepta el nombre `${TEST NAME}` de Robot o un nombre completo único. Si el nombre no corresponde a un caso seleccionado o coincide con más de uno, `build` se detiene. Las asignaciones aparecen en los reportes generados; no modifican `result.json`. Si no indicas opciones, EviDoc usa la configuración local o sus rutas predeterminadas.

## `merge`: resultados de varias ejecuciones (opcional)

```bash
poetry run evidoc merge --input-dir output/primera/metadata --input-dir output/segunda/metadata --output-dir output/final/metadata
poetry run evidoc build --input-dir output/final/metadata --output-dir output/final/reports
```

Repite `--input-dir` en orden cronológico. Si un caso aparece varias veces, se selecciona el último resultado completo. `merge` escribe `merged-results.json` con referencias a la evidencia original. Conserva las carpetas de origen hasta terminar de generar y utilizar los reportes. Si hay una sola ejecución, llama a `build` sobre su carpeta de metadata.

## Documentación e interfaz

```bash
poetry run evidoc docs manual
poetry run evidoc docs library
poetry run evidoc tui
```

`manual` abre el manual offline; `library` abre la referencia de keywords de Robot Framework. `tui` muestra la interfaz interactiva.
