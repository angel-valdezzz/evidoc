# Robot Framework

El listener guarda un `result.json` por prueba. La librería proporciona las keywords para capturar evidencias y registrar archivos descargados.

```bash
poetry run robot --outputdir output/run/robot --listener evidoc.listener tests/
poetry run evidoc build --input-dir output/run/robot/evidoc/metadata --output-dir output/run/robot/evidoc/reports
```

En tu suite o archivo `.resource`:

```robotframework
*** Settings ***
Library    evidoc.robot

*** Test Cases ***
Solicitud completada
    Capture Page Evidence    Credenciales ingresadas    INFO    description=Formulario enviado
    Capture Element Evidence    //div[@id="PanelTitular"]    Titular    INFO    description=Datos confirmados
    Attach File    ${OUTPUT DIR}${/}caratula.pdf    description=Carátula descargada
```

`description` aparece debajo de la imagen en los reportes. `Attach File` registra la ruta absoluta del archivo en la metadata, sin copiarlo ni mostrarlo en el PDF o DOCX. Después de `build`, el archivo aparece en `upload-manifest.json`. Conserva el archivo original para que el proceso posterior pueda leerlo.

También están disponibles `Capture Desktop Evidence`, `Set Defect`, `Log Step`, `Log Info`, `Log Warning`, `Log Error` y las keywords anteriores `Capture Screenshot` y `Attach Artifact`. Esta última copia el archivo a la metadata y conserva su comportamiento previo.

Consulta el [Quick Start](../primeros-pasos/evidencia-robot.md) para opciones de captura, almacenamiento y Pabot. Abre la referencia de todas las keywords con `poetry run evidoc docs robot-library`.
