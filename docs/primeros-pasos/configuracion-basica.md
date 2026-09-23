# Configuracion basica

## Archivos soportados

Evidoc autodetecta estos nombres en el directorio actual:

- `evidoc.toml`
- `evidoc.json`

Si ambos faltan, usa valores por defecto o los sobrescribe con argumentos de CLI/TUI.

## Ejemplo en JSON

```json
{
  "source_dir": "./results",
  "output_dir": "./reports",
  "format": "docx",
  "mode": "single",
  "application": "Portal QA",
  "requirement": "LOGIN-002"
}
```

## Ejemplo en TOML

```toml
source_dir = "./results"
output_dir = "./reports"
format = "pdf"
mode = "run"
application = "Portal QA"
requirement = "LOGIN-002"
```

## Campos validos

| Campo | Tipo | Uso |
| --- | --- | --- |
| `source_dir` | `string` | Directorio donde viven los resultados capturados |
| `output_dir` | `string` | Directorio destino para reportes |
| `format` | `pdf` o `docx` | Formato final del reporte |
| `mode` | `run` o `single` | Consolidado o individual |
| `application` | `string \| null` | Metadato disponible en configuracion |
| `requirement` | `string \| null` | Metadato disponible en configuracion |

!!! tip "Orden de prioridad"
    Los valores pasados por CLI/TUI tienen prioridad sobre el archivo de configuracion cuando se proporcionan explicitamente.

!!! note "Alcance actual"
    El listener toma `application`, `requirement`, `project`, `environment` y `brand` de este archivo y los guarda en cada resultado. `Set Defect` puede añadir la referencia de defecto por caso.

Para los campos nuevos `metadata_dir`, `formats` y `storage`, y la integración directa con `build()`, consulta el [Quick Start de evidencia](evidencia-robot.md).
