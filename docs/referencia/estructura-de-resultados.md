# Estructura de resultados

## Directorios

```text
results/
└── run-<run_id>/
    └── test-<test_id>/
        ├── result.json
        └── artifacts/
            ├── screenshot-....png
            └── archivo-adjunto.ext
```

## Contrato JSON

Campos principales:

- `schema_version`
- `run_id`
- `test_id`
- `generated_at`
- `test_case`
- `steps`
- `artifacts`

## Ejemplo realista

```json
{
  "schema_version": "1.0.0",
  "run_id": "run_20260411_170300",
  "test_id": "login_valid_user",
  "generated_at": "2026-04-11T23:03:17Z",
  "test_case": {
    "name": "User can sign in with valid credentials",
    "status": "PASS",
    "duration": 12.481,
    "application": "Evidence Portal",
    "requirement": "AUTH-LOGIN-001",
    "tags": ["smoke", "auth", "ui"]
  },
  "steps": [
    {
      "title": "Open login page",
      "status": "PASS",
      "logs": [
        {
          "level": "INFO",
          "message": "Navigated to /login",
          "timestamp": "2026-04-11T23:03:06Z"
        }
      ],
      "artifact_ids": ["art_login_page"]
    }
  ],
  "artifacts": [
    {
      "id": "art_login_page",
      "type": "image",
      "path": "artifacts/login-page.png",
      "title": "Login page before submission",
      "description": "Initial state of the authentication form."
    }
  ]
}
```

## Lectura rapida del modelo

| Seccion | Significado |
| --- | --- |
| `test_case` | Metadatos globales de la prueba |
| `steps` | Narrativa secuencial de la ejecucion |
| `logs` | Mensajes asociados al paso actual |
| `artifact_ids` | Vinculo entre paso y evidencia adjunta |
| `artifacts` | Catalogo total de adjuntos |
