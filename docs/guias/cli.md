# Comandos de EviDoc

Ejecuta estos comandos desde el mismo entorno Poetry donde instalaste EviDoc y Robot Framework. El [Quick Start](../primeros-pasos/evidencia-robot.md) muestra cómo configurar las keywords y el listener.

## `build`: reportes y manifiesto

```bash
poetry run evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

`--input-dir` apunta a la metadata del listener o al directorio creado por `merge`. `--output-dir` recibe los reportes y `upload-manifest.json`. `--formats` acepta `pdf`, `docx` o ambos. Sin filtro, se incluyen todos los casos.

Para no generar reportes de casos fallidos u omitidos:

```bash
poetry run evidoc build --input-dir output/final/metadata --output-dir output/final/reports --formats pdf,docx --exclude-status FAIL,SKIP
```

`--exclude-status` acepta un estado o varios separados por coma. El filtro se aplica a los resultados finales **antes** de generar PDF, DOCX y manifiesto. El modo predeterminado es `single` (un reporte por caso); `--mode run` crea uno combinado por formato. Un valor de `mode` en `evidoc.toml` tiene prioridad sobre este predeterminado.

## `merge`: último resultado por caso

```bash
poetry run evidoc merge --input-dir output/run/metadata --input-dir output/rerun/metadata --output-dir output/final/metadata
```

Repite `--input-dir` en orden cronológico. Cuando un caso aparece en ambas entradas, gana el intento completo de la última. `merge` guarda `merged-results.json`, un índice pequeño de los resultados originales; no mueve ni copia capturas. Mantén disponibles las carpetas de entrada hasta terminar `build`. No es necesario ejecutar `merge` si solo hay una tanda de pruebas.

## Configuración y compatibilidad

Si existe `evidoc.toml` o `evidoc.json` en el directorio actual, `build` lee las rutas, formatos, modo y estados excluidos de allí. Los argumentos explícitos prevalecen. El comando anterior `evidoc generate` sigue disponible para los flujos que ya lo utilizan:

```bash
poetry run evidoc generate --source-dir ./results --output-dir ./reports --mode run --format pdf
```

Para abrir la documentación instalada sin servidor:

```bash
poetry run evidoc docs manual
poetry run evidoc docs robot-library
```
