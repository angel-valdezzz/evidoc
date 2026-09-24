# Buenas practicas

## Para que el reporte sea claro y útil

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

## Para mantener calidad tecnica

- Ejecuta `ruff` como linter y formatter de referencia.
- Ejecuta `mypy` antes de fusionar cambios que toquen contratos, renderers o integraciones.
- Ejecuta `import-linter` cuando cambie la relacion entre `domain`, `application`, `infrastructure` o `interfaces`.
- Usa todas las comprobaciones de calidad antes de publicar cambios importantes.

```bash
poetry run ruff check . && poetry run mypy evidoc tests scripts && poetry run lint-imports && poetry run pytest tests/unit -m unit && poetry run pytest tests/acceptance -m acceptance
```

## Para trabajar desde VS Code

- El repositorio ya incluye formato al guardar con Ruff.
- `mypy` queda integrado como proveedor de diagnosticos del workspace.
- `Error Lens` puede mostrar en linea los hallazgos de Ruff y mypy.
- Para ver contratos de arquitectura como diagnosticos del editor, ejecuta la tarea `Import Linter: VSCode diagnostics`.
