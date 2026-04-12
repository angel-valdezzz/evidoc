# Perfiles de uso

## Tester funcional

### Lo teorico

Necesita confirmar que la evidencia existe, es comprensible y termina en un reporte util.

### Lo tecnico

- Normalmente trabajara con TUI o con resultados ya generados por otro equipo.
- Debe reconocer pasos, estados, mensajes y adjuntos.
- Debe validar que el reporte coincide con la ejecucion observada.

## Tester de automatizacion

### Lo teorico

Necesita incrustar captura de evidencia dentro de la automatizacion sin acoplarla demasiado al framework.

### Lo tecnico

- Usara `evidoc.listener` y `evidoc.robot` en Robot Framework.
- O bien consumira `evidoc.api` desde Python.
- Debe decidir donde se guardan resultados y que archivos adjunta.

## Desarrollador

### Lo teorico

Necesita entender el contrato de datos y su traduccion a reportes.

### Lo tecnico

- Trabajara con la API Python y con el esquema JSON.
- Validara que la evidencia generada sea consistente con el dominio.
- Suele depurar problemas de rutas, estados o artefactos faltantes.

## Lider tecnico o QA

### Lo teorico

Necesita gobernar la calidad del uso de Evidoc, no solo ejecutarlo.

### Lo tecnico

- Define convenciones de nombres.
- Revisa estructura de carpetas.
- Estandariza cuando usar `run` vs `single`.
- Determina si la salida debe ser `pdf` o `docx`.
