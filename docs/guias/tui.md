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
| `Bienvenida` | Tab inicial con arte ASCII de `evidoc` y una guia corta de uso |
| `Operacion` | Tab operativo donde se configura y ejecuta la generacion |
| `Report setup` | Formulario principal con origen, destino, formato y modo |
| `Operator checklist` | Resumen de pasos para reducir errores de operacion |
| `status` | Estado actual y resultado de la ultima generacion |

## Atajos de teclado

| Atajo | Accion |
| --- | --- |
| `F1` | Abre el tab `Bienvenida` |
| `F2` | Abre el tab `Operacion` |
| `Ctrl+S` | Abre el selector de carpeta para `source_dir` |
| `Ctrl+O` | Abre el selector de carpeta para `output_dir` |
| `Ctrl+G` | Ejecuta la generacion |

## Seleccion de rutas

Los campos de origen y destino siguen aceptando texto manual, pero ahora tambien ofrecen un boton `Browse` y atajos de teclado para abrir el selector nativo de carpetas en Windows.

## Responsive

Cuando el ancho disponible baja, la TUI apila el formulario y el panel de resumen para evitar cortes de informacion.

## Flujo recomendado

1. Revisa el tab `Bienvenida`.
2. Cambia al tab `Operacion`.
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
