# CLI

El comando nuevo `evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx` genera ambos formatos mediante la misma API de `evidoc.build()`. `generate` continúa disponible. Consulta el [Quick Start](../primeros-pasos/evidencia-robot.md).

## Cuando usarla

Usa la CLI cuando ya tienes resultados capturados y quieres generar reportes de forma reproducible.

## Comando principal

```bash
poetry run evidoc generate --source_dir .\results --output_dir .\reports --mode run --format pdf
```

## Parametros

| Parametro | Requerido | Descripcion |
| --- | --- | --- |
| `--source_dir` | No | Directorio con resultados estructurados |
| `--output_dir` | No | Directorio donde se escriben reportes |
| `--mode` | No | `run` o `single` |
| `--format` | No | `pdf` o `docx` |

## Documentacion integrada

Evidoc distribuye dos recursos de documentacion offline dentro de la instalacion local:

- El manual tecnico generado con MkDocs.
- La referencia de keywords de Robot Framework generada con `libdoc`.

```bash
poetry run evidoc docs manual
```

Ese comando abre la portada del manual offline empaquetado dentro del `wheel`, por lo que sigue disponible despues de `pip install evidoc-...whl` sin depender de un servidor o despliegue web.

```bash
poetry run evidoc docs robot-library
```

## Resultado esperado

- `evidoc docs manual` abre el `index.html` del sitio estatico generado con MkDocs y empaquetado dentro de la instalacion local.
- El comando abre el archivo HTML empaquetado dentro de la instalacion local de Evidoc.
- Ese mismo archivo viaja dentro del wheel, por lo que tambien funciona despues de `pip install evidoc-...whl`.

## Ejemplos practicos

=== "Un PDF consolidado"

    ```bash
    poetry run evidoc generate --source_dir .\results --output_dir .\reports --mode run --format pdf
    ```

=== "Un DOCX por prueba"

    ```bash
    poetry run evidoc generate --source_dir .\results --output_dir .\reports --mode single --format docx
    ```

=== "Usando autodeteccion de `evidoc.json`"

    ```bash
    poetry run evidoc generate
    ```

## Comportamiento observable

- Si no encuentra resultados, imprime `No results found.`
- Si genera salidas, imprime la ruta de cada archivo creado.
- Si abres `docs manual`, imprime la ruta del `index.html` abierto para facilitar soporte y troubleshooting.
- Si abres `docs robot-library`, imprime la ruta del HTML abierto para facilitar soporte y troubleshooting.
- Los argumentos pasados tienen prioridad sobre `evidoc.json` o `evidoc.toml`.

## Comandos de calidad

El flujo de operacion local tambien puede incluir chequeos de calidad antes de generar reportes o publicar cambios.

```bash
poetry run ruff check .
poetry run ruff format .
poetry run mypy evidoc tests scripts
poetry run lint-imports
```

Corrida completa de calidad:

```bash
poetry run ruff check . && poetry run mypy evidoc tests scripts && poetry run lint-imports && poetry run pytest tests/unit -m unit && poetry run pytest tests/acceptance -m acceptance
```

??? info "Buena practica operativa"
    Usa rutas relativas del proyecto cuando compartas comandos con otros equipos. Eso evita que el manual se llene de paths locales irrepetibles.
