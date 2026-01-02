from dataclasses import dataclass
import json
from pathlib import Path

import _exporters


@dataclass
class _CommonTestCaseConfiguration:
    name: str


@dataclass
class SuccessTestCase(_CommonTestCaseConfiguration):
    expected_export_result_file: Path


@dataclass
class FailTestCase(_CommonTestCaseConfiguration):
    error_message: str


type TestCaseRunConfiguration = SuccessTestCase | FailTestCase


def run_integration_test_case(
    run_config: TestCaseRunConfiguration,
    exporter: _exporters.StructurizrWorkspaceExporter,
    workspace_path: Path,
) -> None:
    export_result = exporter.export_to_json(workspace_path)

    match run_config:
        case SuccessTestCase(expected_export_result_file=expected_result_file):
            expected_result = json.loads(expected_result_file.read_text())

            assert not isinstance(
                export_result, _exporters.ExportFailure
            ), "Export result unexpected failed"
            assert (
                export_result == expected_result
            ), "Exported workspace not equals to expected"

        case FailTestCase(error_message=error_message):
            assert isinstance(
                export_result, _exporters.ExportFailure
            ), "Export result unexpected success"
            assert (
                error_message in export_result.error_message
            ), "Stderr doesn't contain error message"


__all__ = [
    "FailTestCase",
    "run_integration_test_case",
    "SuccessTestCase",
    "TestCaseRunConfiguration",
]
