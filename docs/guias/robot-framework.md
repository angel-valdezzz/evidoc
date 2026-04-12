# Robot Framework

## Integraciones disponibles

Evidoc expone dos puntos de integracion para Robot Framework:

- `evidoc.listener` para abrir y cerrar automaticamente el contexto por prueba.
- `evidoc.robot` como libreria de keywords.

## Configuracion minima

```bash
robot --listener evidoc.listener --pythonpath . path\to\tests.robot
```

```robotframework
*** Settings ***
Library    evidoc.robot
```

## Keywords disponibles

| Keyword | Uso |
| --- | --- |
| `Log Step` | Registra un paso |
| `Capture Screenshot` | Captura screenshot desde driver o libreria |
| `Attach Artifact` | Adjunta un archivo |
| `Log Info` | Log informativo |
| `Log Warning` | Log de advertencia |
| `Log Error` | Log de error |

## Ejemplo completo

```robotframework
*** Settings ***
Library    evidoc.robot
Library    examples.robot.support.SupportLibrary

*** Variables ***
${CHECKOUT_TITLE}    Checkout page

*** Test Cases ***
Capture Evidence With Evidoc
    ${artifact_path}=    Create Demo Artifact    ${OUTPUT DIR}${/}sample.txt
    ${driver}=    Get Demo Driver
    Registrar evidencia de checkout    ${driver}    ${artifact_path}

*** Keywords ***
Registrar evidencia de checkout
    [Arguments]    ${driver}    ${artifact_path}
    Log Step    Open checkout    PASS
    Log Info    Entering checkout flow
    Attach Artifact    ${artifact_path}    Input fixture used by the test
    Capture Screenshot    driver=${driver}    title=${CHECKOUT_TITLE}    description=Before submit
    Log Warning    Checkout is slower than expected
    Log Error    Validation summary example
```

## Modo alterno con `library=`

Si el driver vive dentro de otra libreria de Robot:

```robotframework
*** Settings ***
Library    evidoc.robot

*** Test Cases ***
Capture Screenshot From External Library
    Capture Screenshot    library=SeleniumLibrary    title=Resultado visible
```

??? tip "Patron recomendado"
    Usa `Log Step` para dividir la narrativa funcional y luego agrega logs y artefactos dentro de ese paso. Asi el reporte conserva una lectura cronologica clara.
