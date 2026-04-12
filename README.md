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
poetry run evidoc generate --format pdf --mode run
poetry run evidoc generate --format docx --mode single
```

## Robot Framework

```bash
robot --listener evidoc.listener path/to/tests.robot
```
