from evidoc.domain.artifact import Artifact
from evidoc.domain.artifact_id import ArtifactId
from evidoc.domain.evidoc_config import EvidocConfig
from evidoc.domain.log_entry import LogEntry
from evidoc.domain.run import Run
from evidoc.domain.run_id import RunId
from evidoc.domain.run_manifest import RunManifest
from evidoc.domain.schema_version import SCHEMA_VERSION
from evidoc.domain.step import Step
from evidoc.domain.test_case import TestCase
from evidoc.domain.test_id import TestId

ArtifactRef = Artifact
StepResult = Step
TestCaseMetadata = TestCase
TestResult = Run

__all__ = [
    "SCHEMA_VERSION",
    "Artifact",
    "ArtifactId",
    "ArtifactRef",
    "EvidocConfig",
    "LogEntry",
    "Run",
    "RunId",
    "RunManifest",
    "Step",
    "StepResult",
    "TestCase",
    "TestCaseMetadata",
    "TestId",
    "TestResult",
]
