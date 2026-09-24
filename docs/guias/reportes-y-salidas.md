# Reportes y archivos de salida

`build` recibe una carpeta de metadatos y crea un PDF o DOCX por caso de prueba y formato solicitado. El nombre del documento se deriva del nombre del caso, sin identificador de ejecución ni del resultado. Los caracteres incompatibles con los nombres de archivo se sustituyen. Si dos casos generan el mismo nombre seguro en una misma carpeta, `build` se detiene para evitar sobrescribir documentos.

```text
output/evidoc/
├── metadata/
│   └── run-<run_id>/test-<test_id>/result.json
└── reports/
    ├── TC036.pdf
    ├── TC036.docx
    └── upload-manifest.json
```

El manifiesto agrupa por caso los documentos y archivos descargados que registraste con `Attach File`:

```json
{
  "tests": [
    {
      "name": "TC036",
      "files": ["/ruta/absoluta/TC036.pdf", "/ruta/absoluta/caratula.pdf"]
    }
  ]
}
```

Las rutas son absolutas y deben seguir accesibles para la herramienta que las carga. EviDoc no copia ni incrusta los archivos externos en el PDF o Word. Las capturas se muestran como máximo de dos en dos por página, con su descripción debajo. El tamaño de cada imagen conserva sus proporciones.

`--exclude-status FAIL,SKIP` excluye esos casos de los documentos y del manifiesto; conserva los metadatos fuente. Si usas `merge`, su índice final apunta a los resultados originales y las capturas siguen en sus carpetas de ejecución.
