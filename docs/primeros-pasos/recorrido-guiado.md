# Recorrido guiado

## Una sola ejecución

Configura `evidoc.toml` en el directorio donde ejecutarás los comandos:

```toml
metadata_dir = "output/run/robot/evidoc/metadata"
output_dir = "output/run/robot/evidoc/reports"
formats = ["pdf", "docx"]
mode = "single"
```

Ejecuta Robot con el listener e importa la librería de keywords en tu suite:

```bash
poetry run robot --outputdir output/run/robot --listener evidoc.listener tests/
poetry run evidoc build
```

Cada caso genera un PDF y un DOCX con su nombre. `upload-manifest.json` agrupa sus rutas por caso. Si registraste descargas con `Attach File`, también aparecen en `files`.

## Run y rerun

Guarda cada ejecución en carpetas separadas y luego une sus resultados:

```bash
poetry run evidoc merge \
  --input-dir output/run/robot/evidoc/metadata \
  --input-dir output/rerun/robot/evidoc/metadata \
  --output-dir output/final/metadata
poetry run evidoc build \
  --input-dir output/final/metadata \
  --output-dir output/final/reports \
  --exclude-status FAIL,SKIP
```

El resultado del rerun reemplaza al del run para cada prueba repetida. Los casos sin rerun conservan su resultado original. El filtro solo afecta los reportes y el manifiesto; el índice fusionado conserva todos los resultados. No necesitas ejecutar `merge` si hiciste una sola corrida.

Para configurar capturas, descripciones y archivos externos, sigue el [Quick Start](evidencia-robot.md).
