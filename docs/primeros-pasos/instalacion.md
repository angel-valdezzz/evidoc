# Instalación

Necesitas Python 3.11 o posterior compatible con el proyecto de pruebas y Poetry. Coloca el wheel entregado en la carpeta `assets/` de ese proyecto. Ajusta el nombre del archivo a la versión que tengas:

```bash
poetry add ./assets/evidoc-0.1.0-py3-none-any.whl
poetry run evidoc --help
```

Para capturas de página o de un elemento instala `robotframework-seleniumlibrary` en el mismo proyecto:

```bash
poetry add robotframework-seleniumlibrary
```

Las capturas de escritorio necesitan una sesión gráfica activa. Usa `poetry run robot` y `poetry run evidoc` desde el mismo entorno. EviDoc incluye el manual offline y la referencia de keywords:

```bash
poetry run evidoc docs manual
poetry run evidoc docs library
```
