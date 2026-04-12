# Instalacion

## Requisitos

- Python 3.14 disponible en tu entorno
- Poetry 2.x
- Un directorio de trabajo con permisos de escritura para `results/` y `reports/`

## Preparar el entorno

=== "Poetry"

    ```bash
    poetry env use python
    poetry install --with test,acceptance,docs
    ```

=== "Validacion"

    ```bash
    poetry run evidoc --help
    poetry run mkdocs build
    ```

## Que queda instalado

- La CLI `evidoc`
- La interfaz TUI
- La API Python del paquete
- Las dependencias para generar el sitio documental local

!!! note "Sobre el interprete"
    Asegurate de que `python` resuelva al interprete esperado por tu equipo o por el entorno local del proyecto antes de ejecutar `poetry env use python`.
