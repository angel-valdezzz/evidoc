# Reportes y salidas

## Que entra

El insumo real de Evidoc es un conjunto de resultados estructurados en disco.

## Que sale

Segun configuracion, obtendras:

- `pdf` para distribucion fija,
- `docx` para edicion posterior.
- `upload-manifest.json` con las rutas absolutas de los archivos que se entregan por caso.

## Modos de generacion

=== "`mode=run`"

    Genera un reporte consolidado por `run_id`.

=== "`mode=single`"

    Genera un reporte por caso. El archivo toma el nombre seguro del caso, sin `test_id`.

## Ejemplo de salida consolidada

```text
results/
└── run-run_cli/
    ├── test-case_1/
    └── test-case_2/

reports/
└── run-run_cli.pdf
```

## Ejemplo de salida individual

```text
reports/
├── User_can_sign_in.docx
├── Checkout_happy_path.docx
└── upload-manifest.json
```

Si dos casos tienen el mismo nombre seguro dentro de la misma carpeta de metadata, la generacion se detiene para evitar que uno sobrescriba al otro. Guarda ejecuciones distintas en carpetas separadas.

## Resultados fusionados

`evidoc merge` crea `merged-results.json` en el directorio de metadata final. El índice apunta a los resultados de run y rerun, sin duplicar capturas. Al construir los reportes, `--exclude-status FAIL,SKIP` elimina esos casos de los PDF/DOCX y del manifiesto, pero permanecen en la metadata final.

El manifiesto tiene una lista `tests`; cada caso tiene un `name` y un arreglo `files` con las rutas absolutas de sus reportes y archivos registrados mediante `Attach File`. Los archivos externos no se copian ni se incrustan en el documento.

## Que hace un reporte util

- Cada paso se entiende por su titulo.
- Los logs agregan contexto, no ruido.
- Los screenshots tienen `title` y `description`.
- Los archivos adjuntos responden a una necesidad concreta.

!!! note "Fuente de verdad"
    El reporte es una representacion. La evidencia fuente sigue estando en los JSON y en los artefactos guardados en disco.
