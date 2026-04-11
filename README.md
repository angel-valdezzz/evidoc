# Evidoc

Evidoc stores structured test evidence on disk and later generates PDF or DOCX reports.

## Install

```bash
poetry install
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
