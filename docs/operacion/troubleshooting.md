# Solución de problemas

## No se genera ningún reporte

Comprueba que `--input-dir` apunta a la carpeta `metadata` con los `result.json`, o a la carpeta final con `merged-results.json`. Si usaste `--exclude-status`, comprueba que no se filtraron todos los casos. Un `build` sin `merge` funciona con la carpeta de una sola corrida.

## Falta una captura

Usa `Capture Page Evidence`, `Capture Element Evidence` o `Capture Desktop Evidence` con el listener `--listener evidoc.listener`. En las keywords actuales, el nivel se pasa como argumento posicional (`INFO`, `WARN` o `FAIL`); `description=` agrega texto bajo la imagen. Si usas una keyword anterior, comprueba sus argumentos con `poetry run evidoc docs robot-library`.

## Falta un archivo en el manifiesto

Regístralo con `Attach File    ${ruta}` dentro del caso de prueba. El archivo debe existir cuando se llama a la keyword y seguir existiendo al ejecutar `build`. EviDoc informa el caso y la ruta si encuentra una referencia rota. `Attach Artifact` es una keyword anterior: copia el archivo a la metadata y no lo agrega como archivo externo al manifiesto.

## `merge` dice que hay un caso duplicado

Cada carpeta de entrada debe contener un solo resultado por caso. Revisa si reutilizaste la misma carpeta de metadata para varias ejecuciones o si dos casos tienen el mismo nombre completo. Usa carpetas separadas para run y rerun.

## Ya no están las carpetas originales tras `merge`

El índice `merged-results.json` apunta a los `result.json` originales y sus imágenes. Mantén las carpetas de run y rerun disponibles durante `build`; `merge` no duplica esos archivos.

## Dos casos generan el mismo nombre de reporte

EviDoc detiene `build` para evitar sobrescribir un archivo. Diferencia los nombres de los casos que comparten carpeta de salida. En Windows, considera también la longitud total de la ruta del proyecto y del nombre del caso.
