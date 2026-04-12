# TUI

## Cuando usarla

La TUI es util cuando alguien necesita generar reportes sin memorizar comandos, pero aun quiere elegir parametros tecnicos concretos.

## Lanzamiento

```bash
poetry run evidoc tui
```

## Estructura visible

| Seccion | Descripcion |
| --- | --- |
| `Report setup` | Formulario principal con origen, destino, formato y modo |
| `Operator checklist` | Resumen de pasos para reducir errores de operacion |
| `status` | Estado actual y resultado de la ultima generacion |

## Flujo recomendado

1. Define `source_dir`.
2. Define `output_dir`.
3. Elige formato.
4. Elige modo.
5. Revisa el panel lateral para confirmar la operacion.
6. Presiona `Generate report`.

## Que esperar

La interfaz notifica:

- las rutas generadas si hubo reportes,
- o `No results found` si no hay datos validos.

![Captura conceptual de la TUI](../assets/images/tui-wireframe.svg)
