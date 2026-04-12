# Modelo operativo

## Vista teorica

El flujo base siempre es el mismo:

```text
Prueba -> Evidoc captura contexto -> Se escriben resultados en disco -> Evidoc genera reporte
```

La ventaja de este modelo es que desacopla la ejecucion del formato final. Puedes cambiar el framework, el tipo de evidencia o el consumidor del reporte sin romper el contrato de datos.

## Vista tecnica

### 1. Inicio de prueba

Cuando una prueba inicia, Evidoc crea o reutiliza un `run_id` y abre un contexto para un `test_id`.

### 2. Registro de evidencia

Durante la ejecucion se agregan:

- pasos con estado,
- logs con timestamp,
- screenshots,
- archivos adjuntos.

### 3. Cierre de prueba

Al finalizar, se construye un JSON con `schema_version`, `test_case`, `steps` y `artifacts`.

### 4. Generacion de reportes

Luego la CLI o la TUI leen el directorio de resultados y generan:

- un solo reporte por corrida (`mode=run`),
- o un reporte por prueba (`mode=single`).

## Decisiones que afectan el uso

| Decision | Impacto |
| --- | --- |
| `mode=run` | Consolida varias pruebas en un mismo reporte |
| `mode=single` | Facilita compartir evidencia aislada por caso |
| `format=pdf` | Mejor para distribucion y lectura fija |
| `format=docx` | Mejor para edicion o anexos posteriores |

??? tip "Regla practica"
    Si el reporte se enviara tal cual a negocio, empieza con `pdf`. Si otro equipo va a editar el documento despues, usa `docx`.
