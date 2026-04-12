# Evidoc

Evidoc stores structured test evidence on disk and later generates PDF or DOCX reports.

## Install

```bash
poetry install
```

## Tests

The test suite is split into two layers:

- Unit tests in `tests/unit` for domain rules, runtime services, and the framework-agnostic API layer.
- Acceptance tests in `tests/acceptance` using Gherkin/Cucumber-style scenarios executed with `pytest-bdd`.

Install the test dependencies:

```bash
poetry install --with test,acceptance
```

Run the unit suite:

```bash
poetry run pytest tests/unit -m unit
```

Run the acceptance suite:

```bash
poetry run pytest tests/acceptance -m acceptance
```

Run everything with coverage:

```bash
poetry run pytest --cov=evidoc
```

## Generate reports

```bash
poetry run evidoc generate --source_dir ./results --output_dir ./reports --mode run
poetry run evidoc generate --source_dir ./results --output_dir ./reports --mode single
```

## Robot Framework

```bash
robot --listener evidoc.listener --pythonpath . path/to/tests.robot
```

Import the keyword library from Robot:

```robot
*** Settings ***
Library    evidoc.robot
```

Minimal example:

```robot
*** Settings ***
Library    evidoc.robot

*** Test Cases ***
Capture Evidence
    Log Step    Open checkout    PASS
    Log Info    Navigated to checkout
    Attach Artifact    ${CURDIR}${/}sample.txt    Input data
```

An executable end-to-end example with a demo screenshot driver lives at `examples/robot/evidoc_example.robot`.
