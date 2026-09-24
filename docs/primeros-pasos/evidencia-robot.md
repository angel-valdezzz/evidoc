# Registrar evidencia desde Robot Framework

## 1. Prepara el entorno

[Instala el wheel de EviDoc](instalacion.md) en tu proyecto Poetry. Para capturas del navegador, instala SeleniumLibrary en el mismo entorno. Importa ambas bibliotecas en tu archivo `.robot` o en un recurso:

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    evidoc.robot

*** Test Cases ***
Registrar solicitud
    Open Browser    https://example.test    chrome
    Capture Page Evidence    Formulario abierto    INFO    description=El formulario está disponible
    Capture Element Evidence    css:#panel-titular    Datos del titular    INFO    description=Se muestran los datos ingresados
    Close Browser
```

`title` es el encabezado breve; `description=` muestra información adicional debajo de la captura. El segundo argumento posicional es `status` (`INFO`, `WARN`, `FAIL` o `PASS`). También puedes usar `Capture Desktop Evidence` para capturar una aplicación de escritorio. Para registrar un paso sin imagen utiliza `Log Step    Validación terminada    PASS`.

## 2. Ejecuta y construye los documentos

```bash
poetry run robot --outputdir output --listener evidoc.listener tests/
poetry run evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

El listener crea un `result.json` por prueba. `build` genera un PDF y un DOCX por caso y escribe `upload-manifest.json`. El nombre del documento procede del nombre del caso, con los caracteres del sistema de archivos ajustados. Cada página muestra como máximo dos capturas. Si solo ejecutas las pruebas una vez, no necesitas `merge`.

## 3. Registra otros archivos cuando corresponda

Una vez que exista un archivo descargado, registra su ruta final:

```robotframework
Attach File    ${OUTPUT DIR}${/}caratula.pdf    description=Carátula de la póliza
```

`Attach File` registra su ruta absoluta en el resultado. Al construir el manifiesto, EviDoc comprueba que el archivo aún exista y agrega esa misma ruta a `files` del caso. No copia el archivo ni lo incrusta en PDF o Word.

## 4. Añade defectos después de ejecutar

```bash
poetry run evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --defect 'Registrar solicitud=BUG-123'
```

`Registrar solicitud` debe coincidir con `${TEST NAME}`. Si `build` selecciona exactamente un caso, basta `--defect BUG-123`. Cuando hay varios casos, nombra el caso para cada clave. Repite `--defect` para varias claves. Los defectos se escriben en los documentos generados sin modificar la evidencia registrada durante la ejecución.

Consulta [todos los comandos](../guias/cli.md), [todas las keywords](../guias/robot-framework.md) y la [estructura de carpetas](../referencia/estructura-de-resultados.md).
