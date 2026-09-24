# Reportes y salidas

## Que entra

El insumo real de Evidoc es un conjunto de resultados estructurados en disco.

## Que sale

Segun configuracion, obtendras:

- `pdf` para distribucion fija,
- `docx` para edicion posterior.

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
└── Checkout_happy_path.docx
```

Si dos casos tienen el mismo nombre seguro dentro de la misma carpeta de metadata, la generacion se detiene para evitar que uno sobrescriba al otro. Guarda ejecuciones distintas en carpetas separadas.

## Que hace un reporte util

- Cada paso se entiende por su titulo.
- Los logs agregan contexto, no ruido.
- Los screenshots tienen `title` y `description`.
- Los archivos adjuntos responden a una necesidad concreta.

!!! note "Fuente de verdad"
    El reporte es una representacion. La evidencia fuente sigue estando en los JSON y en los artefactos guardados en disco.
