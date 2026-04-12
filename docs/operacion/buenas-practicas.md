# Buenas practicas

## Para que el reporte enganche y no sea ruido

- Cuenta una historia por pasos.
- Adjunta solo evidencia que sirva para defender una conclusion.
- Evita logs repetitivos o de bajo valor.
- Usa nombres de prueba entendibles fuera del equipo tecnico.

## Para que el almacenamiento siga sano

- Separa `results/` de `reports/`.
- Limpia evidencia obsoleta cuando ya no tenga valor operativo.
- Mantiene consistencia en `run_id` y `test_id`.

## Para equipos mixtos

=== "QA manual"

    Prefiere revisar reportes `pdf` y validar que el lenguaje de pasos sea legible.

=== "QA automatizacion"

    Estandariza keywords, nombres de screenshot y descripciones.

=== "Desarrollo"

    Usa la API y revisa JSON cuando el reporte no explique suficiente.
