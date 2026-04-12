# Recorrido guiado

## Objetivo

Generar un reporte a partir de una corrida ya estructurada.

## Paso 1. Revisar la configuracion base

El proyecto incluye un ejemplo funcional en el archivo `evidoc.json` de la raiz.

```json
{
  "source_dir": "./results",
  "output_dir": "./reports",
  "format": "pdf",
  "mode": "run",
  "application": "Example Application",
  "requirement": "REQ-001"
}
```

## Paso 2. Generar por CLI

```bash
poetry run evidoc generate --source_dir .\results --output_dir .\reports --mode run --format pdf
```

## Paso 3. Abrir la TUI

```bash
poetry run evidoc tui
```

La TUI permite seleccionar:

- carpeta de resultados,
- carpeta de salida,
- formato `pdf` o `docx`,
- modo `run` o `single`.

## Paso 4. Entender la salida

Si `mode=run`, obtendras algo como:

```text
reports/
\-- run-run_cli.pdf
```

Si `mode=single`, obtendras un archivo por prueba. El patron de nombre depende del `test_case.name` y del `test_id`.

```text
reports/
|-- User_can_sign_in-login_valid_user.pdf
\-- Checkout_happy_path-checkout_001.pdf
```

??? success "Resultado esperado"
    Si la ejecucion termina sin resultados, la CLI mostrara `No results found.`. Eso no significa error de sistema; normalmente significa que `source_dir` no contiene resultados validos.
