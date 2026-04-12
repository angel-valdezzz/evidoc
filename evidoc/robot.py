from __future__ import annotations

"""<p>Biblioteca de Robot Framework para capturar evidencia con Evidoc.</p>

<p>Utilizala cuando quieras registrar pasos, mensajes, capturas de pantalla o
archivos adjuntos dentro del resultado estructurado de Evidoc.</p>

<h2>Configuracion recomendada</h2>

<p>Importa la biblioteca con:</p>
<pre>Library    evidoc.robot</pre>

<p>Ejecuta Robot Framework con:</p>
<pre>robot --listener evidoc.listener path/to/tests.robot</pre>

<h2>Comportamiento</h2>

<ul>
  <li>Esta biblioteca delega la persistencia en <code>evidoc.api</code>.</li>
  <li>Se recomienda usarla junto con <code>evidoc.listener</code>.</li>
  <li>Si no existe un contexto de prueba activo, Evidoc registra una advertencia.</li>
</ul>
"""

from pathlib import Path
from typing import Any

from robot.api.deco import keyword, library
from robot.libraries.BuiltIn import BuiltIn

from evidoc import api

ROBOT_LIBRARY_SCOPE = "GLOBAL"
ROBOT_AUTO_KEYWORDS = False
ROBOT_LIBRARY_DOC_FORMAT = "HTML"


@library(scope="GLOBAL", auto_keywords=False)
class RobotLibrary:
    """<p>Biblioteca principal de keywords expuesta por Evidoc.</p>

    <h2>Uso recomendado</h2>

    <p>Importacion:</p>
    <pre>Library    evidoc.robot</pre>

    <p>Ejecucion:</p>
    <pre>robot --listener evidoc.listener path/to/tests.robot</pre>

    <h2>Nota operativa</h2>

    <p>Las keywords escriben evidencia sobre el contexto de prueba activo. Si no
    existe un contexto abierto, la API subyacente registra una advertencia.</p>
    """

    @keyword("Log Step")
    def log_step(self, title: str, status: str = "INFO") -> None:
        """<p>Registra un paso visible dentro de la narrativa de la prueba.</p>

        <h2>Argumentos</h2>
        <ul>
          <li><b>title</b>: texto que se mostrara como nombre del paso.</li>
          <li><b>status</b>: estado del paso. Los valores mas comunes son PASS, FAIL,
          WARN e INFO.</li>
        </ul>

        <h2>Recomendacion</h2>
        <p>Usa esta keyword para dividir la evidencia en hitos faciles de leer.</p>
        """
        api.log_step(title, status)

    @keyword("Capture Screenshot")
    def capture_screenshot(
        self,
        driver: Any | None = None,
        element: Any | None = None,
        title: str | None = None,
        description: str | None = None,
        library: str | None = None,
    ) -> str | None:
        """<p>Captura una imagen desde un driver o desde otra libreria de Robot.</p>

        <h2>Argumentos</h2>
        <ul>
          <li><b>driver</b>: objeto que ya expone una operacion de screenshot.</li>
          <li><b>element</b>: elemento opcional para capturar una region especifica.</li>
          <li><b>title</b>: titulo visible del artefacto generado.</li>
          <li><b>description</b>: descripcion complementaria para el reporte.</li>
          <li><b>library</b>: nombre de la libreria de Robot desde la que se resolvera
          la instancia real del driver.</li>
        </ul>

        <h2>Uso</h2>
        <ul>
          <li>Usa <code>driver</code> cuando ya tienes acceso directo al objeto.</li>
          <li>Usa <code>library</code> cuando el driver vive dentro de otra libreria,
          por ejemplo <code>SeleniumLibrary</code>.</li>
        </ul>

        <h2>Retorno</h2>
        <p>Retorna el identificador del artefacto cuando la captura se registra
        correctamente.</p>
        """
        target = driver
        if library:
            target = BuiltIn().get_library_instance(library)
        if target is None:
            raise ValueError("Capture Screenshot requires a driver or an explicit library name.")
        return api.capture_screenshot(target, element=element, title=title, description=description)

    @keyword("Attach Artifact")
    def attach_artifact(self, path: str | Path, description: str | None = None) -> str | None:
        """<p>Adjunta un archivo local existente a la prueba activa.</p>

        <h2>Argumentos</h2>
        <ul>
          <li><b>path</b>: ruta absoluta o relativa al directorio de ejecucion.</li>
          <li><b>description</b>: contexto opcional que se mostrara en el reporte.</li>
        </ul>

        <h2>Retorno</h2>
        <p>Retorna el identificador del artefacto almacenado cuando el archivo se
        acepta correctamente.</p>
        """
        return api.attach_artifact(path, description)

    @keyword("Log Info")
    def log_info(self, message: str) -> None:
        """<p>Agrega un mensaje informativo al paso actual.</p>"""
        api.log_info(message)

    @keyword("Log Warning")
    def log_warning(self, message: str) -> None:
        """<p>Agrega un mensaje de advertencia al paso actual.</p>"""
        api.log_warning(message)

    @keyword("Log Error")
    def log_error(self, message: str) -> None:
        """<p>Agrega un mensaje de error al paso actual.</p>"""
        api.log_error(message)


_LIBRARY = RobotLibrary()


@keyword("Log Step")
def log_step(title: str, status: str = "INFO") -> None:
    _LIBRARY.log_step(title, status)


@keyword("Capture Screenshot")
def capture_screenshot(
    driver: Any | None = None,
    element: Any | None = None,
    title: str | None = None,
    description: str | None = None,
    library: str | None = None,
) -> str | None:
    return _LIBRARY.capture_screenshot(
        driver=driver,
        element=element,
        title=title,
        description=description,
        library=library,
    )


@keyword("Attach Artifact")
def attach_artifact(path: str | Path, description: str | None = None) -> str | None:
    return _LIBRARY.attach_artifact(path, description)


@keyword("Log Info")
def log_info(message: str) -> None:
    _LIBRARY.log_info(message)


@keyword("Log Warning")
def log_warning(message: str) -> None:
    _LIBRARY.log_warning(message)


@keyword("Log Error")
def log_error(message: str) -> None:
    _LIBRARY.log_error(message)
