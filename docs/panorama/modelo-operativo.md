# Modelo operativo

EviDoc registra evidencias mientras se ejecuta cada prueba y construye los documentos una vez guardados los resultados:

1. El listener de Robot Framework o la API Python inicia el caso y registra su nombre.
2. Las keywords o la API guardan pasos, mensajes, capturas y rutas de otros archivos.
3. Al terminar el caso se escribe `result.json` con su estado y su evidencia.
4. `build` lee los resultados seleccionados y crea un PDF o DOCX por caso, además de `upload-manifest.json`.

Cada resultado contiene `run_id` y `test_id` para identificar la ejecución y sus archivos internos. Los nombres de PDF y DOCX derivan solamente del nombre del caso. Los archivos descargados registrados con `Attach File` permanecen en su ruta original.

Si tienes varias ejecuciones del mismo conjunto de pruebas, puedes usar `merge` para seleccionar el último resultado completo de cada caso antes de `build`. `merge` no es necesario cuando trabajas con una sola ejecución.

| Opción | Efecto |
| --- | --- |
| `--formats pdf,docx` | Selecciona los documentos que se producen por caso. |
| `--exclude-status FAIL,SKIP` | Deja esos casos fuera de los documentos y del manifiesto. |
| `--defect 'Caso=BUG-123'` | Muestra una clave de defecto para el caso indicado en los documentos, sin modificar `result.json`. |
