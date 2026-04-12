# TUI

## Cuando usarla

La TUI es util cuando alguien necesita generar reportes sin memorizar comandos, pero aun quiere elegir parametros tecnicos concretos.

## Lanzamiento

```bash
poetry run evidoc tui
```

## Compatibilidad visual

La interfaz usa bordes ASCII en sus paneles y controles principales para mantener una presentacion consistente en el CMD basico de Windows.

## Estructura visible

| Seccion | Descripcion |
| --- | --- |
| `Bienvenida` | Pestania inicial con arte ASCII de `evidoc` y una guia corta de uso |
| `Generacion` | Pestania operativa donde se configura y ejecuta la generacion |
| `Report setup` | Formulario principal con origen, destino, formato y modo |
| `Operator checklist` | Resumen de pasos para reducir errores de operacion |
| `status` | Estado actual y resultado de la ultima generacion |

## Flujo recomendado

1. Revisa la pestania `Bienvenida`.
2. Cambia a la pestania `Generacion`.
3. Define `source_dir`.
4. Define `output_dir`.
5. Elige formato.
6. Elige modo.
7. Revisa el panel lateral para confirmar la operacion.
8. Presiona `Generate report`.

## Que esperar

La interfaz notifica:

- las rutas generadas si hubo reportes,
- o `No results found` si no hay datos validos.

![Captura conceptual de la TUI](../assets/images/tui-wireframe.svg)
