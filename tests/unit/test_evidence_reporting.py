from __future__ import annotations

from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from io import BytesIO
from pathlib import Path

import pytest
from docx import Document
from evidoc import build
from evidoc.api import EvidocAPI
from evidoc.infrastructure.bootstrap import project_root
from evidoc.infrastructure.filesystem.filesystem_result_repository import FilesystemResultRepository
from evidoc.infrastructure.reporting.helpers import fitted_size
from evidoc.interfaces.cli.main import app
from evidoc.listener import Listener
from PIL import Image
from robot.run import run
from typer.testing import CliRunner


def png() -> bytes:
    stream = BytesIO()
    Image.new("RGB", (80, 50), "blue").save(stream, format="PNG")
    return stream.getvalue()


def write_worker(root: Path, number: int) -> None:
    api = EvidocAPI(root_dir=root)
    api.start_test(f"Process {number}")
    api.capture_image(png(), title=f"Evidence {number}")
    api.end_test("PASS", 0.1)


@pytest.mark.parametrize("storage", ["file", "base64"])
def test_storage_and_both_renderers(tmp_path: Path, storage: str) -> None:
    source = tmp_path / "metadata"
    api = EvidocAPI(root_dir=source, storage=storage, application="Portal", requirement="REQ-9")
    api.start_test("Inicio de sesión")
    for kind in ("page", "element", "desktop"):
        assert api.capture_image(png(), title=kind, capture=kind, orientation="horizontal")
    api.end_test("PASS", 1.5)
    results = FilesystemResultRepository(
        project_root() / "schemas" / "result.schema.json"
    ).load_test_results(source)
    assert len(results) == 1
    assert [step.title for step in results[0].steps] == ["page", "element", "desktop"]
    result = results[0]
    assert all(bool(a.data) == (storage == "base64") for a in result.artifacts)
    assert len(list(source.rglob("*.png"))) == (0 if storage == "base64" else 3)
    outputs = build(source, tmp_path / "reports", ["pdf", "docx"])
    assert {output.suffix for output in outputs} == {".pdf", ".docx"}
    assert all(output.stat().st_size > 1000 for output in outputs)
    document = Document(str(next(p for p in outputs if p.suffix == ".docx")))
    assert "Reporte de Ejecución Automatizada" in [p.text for p in document.paragraphs]
    assert "Portal" in [cell.text for row in document.tables[0].rows for cell in row.cells]
    assert len(document.inline_shapes) == 3
    assert [row.cells[0].text for row in document.tables[0].rows][-1] == "Defecto"
    assert document.tables[0].rows[-1].cells[1].text == ""
    assert 'w:fill="C62828"' in document.tables[0].rows[-1].cells[0]._tc.xml
    from pypdf import PdfReader

    pdf_text = "\n".join(
        page.extract_text()
        for page in PdfReader(next(p for p in outputs if p.suffix == ".pdf")).pages
    )
    assert "Resumen De Ejecución" in pdf_text
    assert pdf_text.index("page") < pdf_text.index("element") < pdf_text.index("desktop")


def test_cli_and_python_build_match(tmp_path: Path) -> None:
    source = tmp_path / "metadata"
    api = EvidocAPI(root_dir=source)
    api.start_test("Caso")
    api.capture_image(png(), title="Pantalla")
    api.end_test("PASS", 0.2)
    expected = build(source, tmp_path / "python", ["pdf", "docx"])
    result = CliRunner().invoke(
        app,
        [
            "build",
            "--input-dir",
            str(source),
            "--output-dir",
            str(tmp_path / "cli"),
            "--formats",
            "pdf,docx",
        ],
    )
    assert result.exit_code == 0, result.stdout
    assert {p.name for p in expected} == {p.name for p in (tmp_path / "cli").iterdir()}


def test_robot_run_listener_and_capture_adapters(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    class Element:
        screenshot_as_png = png()

    class Selenium:
        driver = Element()

        def find_element(self, locator: str) -> Element:
            assert locator == "//div[@id='PanelTitular']"
            return Element()

    monkeypatch.setattr("evidoc.robot.BuiltIn.get_library_instance", lambda self, name: Selenium())
    monkeypatch.setattr("evidoc.robot.desktop_bytes", png)
    suite = tmp_path / "suite.robot"
    suite.write_text(
        """*** Settings ***
Library    evidoc.robot
*** Test Cases ***
Capture all
    Capture Page Evidence    Credenciales ingresadas    INFO
    Capture Element Evidence    //div[@id='PanelTitular']    Panel Titular    INFO    orientation=horizontal    include_page=True
    Capture Desktop Evidence    Evidencia completa    INFO
""",
        encoding="utf-8",
    )
    output = tmp_path / "output"
    assert (
        run(
            str(suite), listener="evidoc.listener", outputdir=str(output), log="NONE", report="NONE"
        )
        == 0
    )
    results = FilesystemResultRepository(
        project_root() / "schemas" / "result.schema.json"
    ).load_test_results(output / "evidoc" / "metadata")
    assert len(results) == 1
    assert [a.capture for a in results[0].artifacts] == ["page", "page", "element", "desktop"]
    assert results[0].artifacts[2].orientation == "horizontal"
    assert results[0].steps[1].title == "Contexto: Panel Titular"


def test_small_element_uses_available_report_space() -> None:
    assert fitted_size(80, 50, 480, 340) == (480, 300)
    assert fitted_size(800, 50, 480, 340) == (480, 30)


def test_toml_config_applies_to_listener_and_build(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.chdir(tmp_path)
    (tmp_path / "evidoc.toml").write_text(
        'aplicacion = "Salud"\nproyecto = "Espartaco"\nenvironment = "QA"\nbrand = "AXA"\n'
        'formats = ["pdf", "docx"]\nstorage = "base64"\nmetadata_dir = "metadata"\n'
        'output_dir = "reports"\n',
        encoding="utf-8",
    )
    monkeypatch.setattr("evidoc.robot.desktop_bytes", png)
    suite = tmp_path / "test.robot"
    suite.write_text(
        "*** Settings ***\nLibrary    evidoc.robot\n*** Test Cases ***\nCaso real\n"
        "    Set Defect    BUG-17\n    Capture Desktop Evidence    Evidencia\n",
        encoding="utf-8",
    )
    assert (
        run(
            str(suite),
            listener=Listener(),
            outputdir=str(tmp_path / "robot"),
            log="NONE",
            report="NONE",
        )
        == 0
    )
    results = FilesystemResultRepository(
        project_root() / "schemas" / "result.schema.json"
    ).load_test_results(tmp_path / "metadata")
    assert len(results) == 1
    assert results[0].test_case.application == "Salud"
    assert results[0].test_case.project == "Espartaco"
    assert results[0].test_case.defect == "BUG-17"
    assert results[0].artifacts[0].data
    outputs = build()
    assert {output.suffix for output in outputs} == {".pdf", ".docx"}
    assert all(output.parent.resolve() == tmp_path / "reports" for output in outputs)
    cli = CliRunner().invoke(app, ["build", "--output-dir", str(tmp_path / "cli-reports")])
    assert cli.exit_code == 0, cli.stdout
    assert {output.name for output in outputs} == {
        output.name for output in (tmp_path / "cli-reports").iterdir()
    }


def test_robot_listener_storage_configuration(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setattr("evidoc.robot.desktop_bytes", png)
    suite = tmp_path / "desktop.robot"
    suite.write_text(
        "*** Settings ***\nLibrary    evidoc.robot\n*** Test Cases ***\nCase\n    Capture Desktop Evidence    Escritorio\n",
        encoding="utf-8",
    )
    metadata = tmp_path / "shared" / "metadata"
    assert (
        run(
            str(suite),
            listener=Listener(root_dir=str(metadata), storage="base64"),
            outputdir=str(tmp_path / "robot"),
            log="NONE",
            report="NONE",
        )
        == 0
    )
    results = FilesystemResultRepository(
        project_root() / "schemas" / "result.schema.json"
    ).load_test_results(metadata)
    assert len(results) == 1
    assert results[0].artifacts[0].data
    assert not list(metadata.rglob("*.png"))


def test_missing_capture_adapter_warns_without_failing_robot(tmp_path: Path) -> None:
    suite = tmp_path / "no_browser.robot"
    suite.write_text(
        "*** Settings ***\nLibrary    evidoc.robot\n*** Test Cases ***\nCase\n    Capture Page Evidence    Sin navegador\n",
        encoding="utf-8",
    )
    output = tmp_path / "output"
    assert (
        run(
            str(suite), listener="evidoc.listener", outputdir=str(output), log="NONE", report="NONE"
        )
        == 0
    )
    results = FilesystemResultRepository(
        project_root() / "schemas" / "result.schema.json"
    ).load_test_results(output / "evidoc" / "metadata")
    assert len(results) == 1
    assert not results[0].artifacts


def test_concurrent_writers_share_run_without_overwriting(tmp_path: Path) -> None:
    root = tmp_path / "metadata"

    def worker(i: int) -> None:
        api = EvidocAPI(root_dir=root)
        api.start_test(f"Case {i}")
        api.capture_image(png(), title=f"Evidence {i}")
        api.end_test("PASS", 0.1)

    with ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(worker, range(24)))
    results = FilesystemResultRepository(
        project_root() / "schemas" / "result.schema.json"
    ).load_test_results(root)
    assert len(results) == 24
    assert len({r.run_id for r in results}) == 1
    assert len({r.test_id for r in results}) == 24


def test_separate_processes_share_metadata_directory(tmp_path: Path) -> None:
    root = tmp_path / "metadata"
    with ProcessPoolExecutor(max_workers=4) as pool:
        list(pool.map(write_worker, [root] * 12, range(12)))
    results = FilesystemResultRepository(
        project_root() / "schemas" / "result.schema.json"
    ).load_test_results(root)
    assert len(results) == 12
    assert len({result.run_id for result in results}) == 1
