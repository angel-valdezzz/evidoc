# Instalacion

## Requisitos

- Python 3.14 disponible en `C:\Users\Casa\AppData\Local\Programs\Python\Python314\python.exe`
- Poetry 2.x
- Un directorio de trabajo con permisos de escritura para `results/` y `reports/`

## Preparar el entorno

=== "Poetry"

    ```powershell
    Set-Alias python "C:\Users\Casa\AppData\Local\Programs\Python\Python314\python.exe"
    poetry env use python
    poetry install --with test,acceptance,docs
    ```

=== "Validacion"

    ```powershell
    poetry run evidoc --help
    poetry run mkdocs build
    ```

## Que queda instalado

- La CLI `evidoc`
- La interfaz TUI
- La API Python del paquete
- Las dependencias para generar el sitio documental local

!!! note "Sobre el alias `python`"
    En PowerShell el alias se define por sesion. Si abres otra terminal, vuelvelo a crear antes de ejecutar `poetry env use python`.
