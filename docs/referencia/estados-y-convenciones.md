# Estados y convenciones

## Estados soportados

| Estado | Uso recomendado |
| --- | --- |
| `PASS` | El paso o prueba cumple lo esperado |
| `FAIL` | Existe un error funcional o tecnico |
| `WARN` | Hay hallazgo relevante sin romper la ejecucion |
| `INFO` | Mensaje neutro o contextual |
| `SKIP` | La prueba no se ejecuto o se omitio |

## Convenciones recomendadas

### Nombres de prueba

- Hazlos legibles para negocio.
- Evita IDs crudos como unico contexto.

### Pasos

- Empieza con verbo: `Open checkout`, `Submit credentials`, `Validate banner`.
- Un paso debe describir una accion o una verificacion, no todo el caso.

### Adjuntos

- Da `description` cuando el archivo no sea obvio.
- Usa screenshots para estado visual.
- Usa archivos para logs, payloads y fixtures.

### Logs

- `INFO` para narrativa normal.
- `WARN` para degradaciones o desviaciones.
- `FAIL` o `Log Error` cuando el hecho representa un problema real.
