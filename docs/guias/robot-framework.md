# Robot Framework

Importa `Library    evidoc.robot` en la suite o en un recurso. Ejecuta Robot con `--listener evidoc.listener` para que EviDoc abra y cierre automáticamente cada caso de prueba:

```bash
poetry run robot --outputdir output --listener evidoc.listener tests/
```

| Keyword | Argumentos principales | Función |
| --- | --- | --- |
| `Capture Page Evidence` | `title`, `status=INFO`, `orientation=None`, `description=None` | Captura la página con SeleniumLibrary. |
| `Capture Element Evidence` | `locator`, `title`, `status=INFO`, `orientation=None`, `include_page=False`, `description=None` | Captura un elemento; `include_page=True` agrega una imagen de contexto. |
| `Capture Desktop Evidence` | `title`, `status=INFO`, `orientation=None`, `description=None` | Captura el escritorio activo. |
| `Log Step` | `title`, `status=INFO` | Registra un paso sin imagen. |
| `Log Info`, `Log Warning`, `Log Error` | `message` | Agrega un mensaje al paso. |
| `Attach File` | `path`, `description=None` | Registra la ruta absoluta de un archivo para el manifiesto, sin copiarlo. |
| `Capture Screenshot` | `driver`, `element`, `title`, `description`, `library` | Captura desde un controlador o biblioteca disponible; consulta la referencia para los parámetros. |

Las keywords de capturas usan `status` como argumento posicional y admiten `description=` como argumento con nombre. El título debe ser breve; la descripción aparece debajo de la imagen. Para capturas de página y elemento debe existir una instancia activa de SeleniumLibrary. Puedes consultar firmas y descripciones desde `poetry run evidoc docs library`.

[Guía paso a paso](../primeros-pasos/evidencia-robot.md) · [Archivos de salida](reportes-y-salidas.md)
