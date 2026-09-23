# Quick Start: evidencia de Robot a PDF y Word

Instala EviDoc en el mismo entorno de Python donde ejecutas Robot. Para capturas del navegador instala también SeleniumLibrary; para escritorio debe haber una sesión gráfica activa. El listener y las keywords son independientes: carga ambos.

```robotframework
*** Settings ***
Library    SeleniumLibrary
Library    evidoc.robot

*** Test Cases ***
Solicitud del titular
    Open Browser    https://example.org    chrome
    Capture Page Evidence    Credenciales ingresadas    INFO
    Capture Element Evidence    //div[@id="PanelTitular"]    Panel Titular    INFO
    Capture Desktop Evidence    Evidencia completa    INFO
    Close Browser
```

Sustituye la URL y el locator del ejemplo por los de tu aplicación. Las capturas de página usan el viewport del navegador activo en SeleniumLibrary; las de elemento usan su locator (incluidos prefijos como `css:` o `xpath:`); las de escritorio usan la pantalla completa del sistema y pueden incluir barra de direcciones, fecha y otras ventanas. `orientation=horizontal` o `orientation=vertical` es opcional y ajusta el espacio reservado para la imagen en el reporte. La captura de escritorio puede fallar sin sesión gráfica (por ejemplo, un agente CI sin display); EviDoc registra una advertencia sin fallar el caso.

## Listener y directorios

```bash
robot --outputdir output --listener evidoc.listener tests/
evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

El listener toma `${OUTPUT DIR}` de Robot. Por defecto escribe `output/evidoc/metadata/run-<id>/test-<id>/result.json`; con almacenamiento `file`, la misma carpeta contiene `artifacts/*.png`. Los informes se generan en `output/evidoc/reports` al ejecutar `build`. Robot continúa escribiendo `output.xml`, `log.html` y `report.html` directamente en `output`.

La configuración opcional del listener usa los argumentos posicionales de Robot, en este orden: `root_dir`, `storage`, `application`, `requirement`. Para cambiar storage y mantener el directorio por defecto, indica explícitamente el directorio:

```bash
robot --outputdir output --listener evidoc.listener.Listener:output/evidoc/metadata:base64:VisualTime:REQ-123 tests/
```

En Windows, Robot separa argumentos de listener con `:`; si la ruta incluye letra de unidad, usa una ruta relativa o una instancia Python del listener. Para Pabot, usa **el mismo directorio de metadata absoluto o relativo al cwd** en todos los workers y construye los reportes tras terminar todos los procesos:

```bash
pabot --outputdir output --listener evidoc.listener.Listener:output/evidoc/metadata:file tests/
evidoc build --input-dir output/evidoc/metadata --output-dir output/evidoc/reports --formats pdf,docx
```

Cada caso tiene un ID único. El ID de ejecución se crea atómicamente y se comparte por los workers que apuntan al mismo directorio. Usa un directorio nuevo por ejecución para no mezclar resultados anteriores.

## Python sin subprocess

```python
from robot import run
from evidoc import build

code = run("tests", outputdir="output", listener="evidoc.listener")
reports = build(
    input_dir="output/evidoc/metadata",
    output_dir="output/evidoc/reports",
    formats=["pdf", "docx"],
)
print(code, reports)
```

`build()` retorna una lista de `Path`. El modo por defecto genera un PDF y un DOCX por caso; `mode="run"` genera un documento por formato para todos los casos. `evidoc generate` permanece disponible para los flujos anteriores.

## Almacenamiento y metadatos

`file` guarda PNG independientes y su ruta relativa en `result.json`. `base64` incrusta los bytes de cada PNG en `data` y evita crear PNG separados. Los adjuntos no fotográficos siguen siendo archivos. Ambos formatos de reporte usan el mismo modelo de resultado y aceptan ambas estrategias. PDF es el documento de entrega; DOCX conserva tablas, textos e imágenes editables en Word.

Los artefactos de imagen registran `capture` (`page`, `element` o `desktop`) y `orientation`. Los pasos y sus referencias a artefactos conservan el orden en que se invocaron las keywords. Las APIs anteriores `Capture Screenshot`, `Log Step`, `Log Info`, `Attach Artifact` y `evidoc generate` siguen disponibles.
