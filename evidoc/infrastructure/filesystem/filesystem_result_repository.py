from __future__ import annotations

import json
import time
from pathlib import Path
from uuid import uuid4

from jsonschema import validate

from evidoc.application.located_result import LocatedResult
from evidoc.application.result_repository import ResultRepository
from evidoc.domain.contracts import run_from_dict
from evidoc.domain.run import Run


class FilesystemResultRepository(ResultRepository):
    def __init__(self, result_schema_path: Path) -> None:
        self._result_schema = json.loads(result_schema_path.read_text(encoding="utf-8"))

    def get_or_create_run_id(self, root_dir: Path) -> str:
        root_dir.mkdir(parents=True, exist_ok=True)
        run_id_file = root_dir / ".run_id"
        if run_id_file.exists():
            return self._read_run_id(run_id_file)
        run_id = uuid4().hex[:12]
        try:
            with run_id_file.open("x", encoding="utf-8") as handle:
                handle.write(run_id)
            return run_id
        except FileExistsError:
            return self._read_run_id(run_id_file)

    @staticmethod
    def _read_run_id(path: Path) -> str:
        # Another worker may have created the file but not written its content yet.
        for _ in range(100):
            value = path.read_text(encoding="utf-8").strip()
            if value:
                return value
            time.sleep(0.01)
        raise RuntimeError(f"Run ID was not initialized: {path}")

    def save_test_result(self, root_dir: Path, result: Run) -> Path:
        test_dir = root_dir / f"run-{result.run_id}" / f"test-{result.test_id}"
        test_dir.mkdir(parents=True, exist_ok=True)
        payload = result.to_dict()
        validate(payload, self._result_schema)
        result_path = test_dir / "result.json"
        result_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        return result_path

    def load_test_results(self, source_dir: Path) -> list[Run]:
        return [located.result for located in self.load_located_results(source_dir)]

    def load_located_results(self, source_dir: Path) -> list[LocatedResult]:
        if not source_dir.exists():
            return []
        index = source_dir / "merged-results.json"
        if index.is_file():
            payload = json.loads(index.read_text(encoding="utf-8"))
            if payload.get("schema_version") != "1.0" or not isinstance(
                payload.get("results"), list
            ):
                raise ValueError(f"Invalid merged metadata index: {index}")
            paths = [Path(entry["path"]) for entry in payload["results"]]
        else:
            paths = sorted(source_dir.glob("run-*/test-*/result.json"))
        results: list[LocatedResult] = []
        for result_path in paths:
            if result_path.name != "result.json" or not result_path.is_file():
                raise ValueError(f"Missing result referenced by merged metadata: {result_path}")
            payload = json.loads(result_path.read_text(encoding="utf-8"))
            validate(payload, self._result_schema)
            result = self._from_dict(payload)
            results.append(
                LocatedResult(result, result_path.resolve(), result_path.resolve().parents[2])
            )
        if index.is_file():
            return results
        return sorted(
            results, key=lambda located: (located.result.generated_at, located.result.test_id)
        )

    def save_merged_results(self, output_dir: Path, results: list[LocatedResult]) -> Path:
        output_dir.mkdir(parents=True, exist_ok=True)
        path = output_dir / "merged-results.json"
        payload = {
            "schema_version": "1.0",
            "results": [{"path": str(located.result_path)} for located in results],
        }
        temporary = path.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
        temporary.replace(path)
        return path

    def _from_dict(self, payload: dict) -> Run:
        return run_from_dict(payload)
