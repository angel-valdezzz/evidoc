# CLI

## Cuando usarla

Usa la CLI cuando ya tienes resultados capturados y quieres generar reportes de forma reproducible.

## Comando principal

```powershell
poetry run evidoc generate --source_dir .\results --output_dir .\reports --mode run --format pdf
```

## Parametros

| Parametro | Requerido | Descripcion |
| --- | --- | --- |
| `--source_dir` | No | Directorio con resultados estructurados |
| `--output_dir` | No | Directorio donde se escriben reportes |
| `--mode` | No | `run` o `single` |
| `--format` | No | `pdf` o `docx` |

## Ejemplos practicos

=== "Un PDF consolidado"

    ```powershell
    poetry run evidoc generate --source_dir .\results --output_dir .\reports --mode run --format pdf
    ```

=== "Un DOCX por prueba"

    ```powershell
    poetry run evidoc generate --source_dir .\results --output_dir .\reports --mode single --format docx
    ```

=== "Usando autodeteccion de `evidoc.json`"

    ```powershell
    poetry run evidoc generate
    ```

## Comportamiento observable

- Si no encuentra resultados, imprime `No results found.`
- Si genera salidas, imprime la ruta de cada archivo creado.
- Los argumentos pasados tienen prioridad sobre `evidoc.json` o `evidoc.toml`.

??? info "Buena practica operativa"
    Usa rutas relativas del proyecto cuando compartas comandos con otros equipos. Eso evita que el manual se llene de paths locales irrepetibles.
