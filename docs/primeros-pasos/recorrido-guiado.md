# Recorrido guiado

1. [Instala EviDoc](instalacion.md) en el entorno Poetry de tus pruebas.
2. [Registra evidencia con Robot](evidencia-robot.md) y ejecuta las pruebas con el listener.
3. Genera los documentos a partir de la carpeta de metadatos:

```bash
poetry run robot --outputdir output --listener evidoc.listener tests/
poetry run evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

El segundo comando produce un documento por caso y `upload-manifest.json` con las rutas absolutas de los archivos a cargar. Si descubres un defecto después de la ejecución, repite `build` con `--defect 'Nombre del caso=BUG-123'`. Puedes excluir casos con `--exclude-status FAIL,SKIP`.

Cuando necesites combinar los resultados de varias ejecuciones, consulta [`merge`](../guias/cli.md#merge-resultados-de-varias-ejecuciones-opcional). Ese comando es opcional; no hace falta para generar reportes de una sola ejecución.
