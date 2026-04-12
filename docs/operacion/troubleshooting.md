# Troubleshooting

## `No results found.`

Posibles causas:

- `source_dir` apunta a una carpeta equivocada.
- No existen `result.json` validos.
- La corrida no llego a persistirse.

## No aparece un screenshot

Revisa:

- si habia una prueba activa,
- si el driver implementa `screenshot()` o `save_screenshot()`,
- si la ruta de artefactos pudo escribirse.

## Un archivo no se adjunta

La causa mas comun es simple: el path no existe al momento de llamar `attach_file()` o `Attach Artifact`.

## El reporte sale en un formato distinto al esperado

Prioridad de revision:

1. Argumentos pasados en CLI o TUI.
2. Configuracion en `evidoc.json` o `evidoc.toml`.
3. Verifica que hayas pedido `--format docx` o `--format pdf`.

## La evidencia se genera, pero la narrativa es pobre

Eso suele ser un problema de uso, no del motor:

- faltan `Log Step`,
- los mensajes son demasiado tecnicos,
- los adjuntos no tienen titulo ni descripcion suficiente.
