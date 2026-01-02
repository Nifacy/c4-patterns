from dataclasses import dataclass
import json
from pathlib import Path
import _integration_test_runner


@dataclass(frozen=True, slots=True)
class _TestCaseInfo:
    name: str
    workspace_path: Path
    run_config: _integration_test_runner.TestCaseRunConfiguration


def extract_test_cases_info_from_file(config_file: Path) -> list[_TestCaseInfo]:
    raw_infos = json.loads(config_file.read_text())
    test_cases_info: list[_TestCaseInfo] = []

    for raw_info in raw_infos:
        match raw_info:
            case {
                "result": "success",
                "name": str(name),
                "workspace": str(workspace_path),
                "export_result_file": str(result_file_path),
            }:
                test_cases_info.append(
                    _TestCaseInfo(
                        name=name,
                        workspace_path=Path(workspace_path),
                        run_config=_integration_test_runner.SuccessTestCase(
                            name=name,
                            expected_export_result_file=Path(result_file_path),
                        ),
                    )
                )

            case {
                "result": "fail",
                "name": str(name),
                "workspace": str(workspace_path),
                "error_message": str(error_message),
            }:
                test_cases_info.append(
                    _TestCaseInfo(
                        name=name,
                        workspace_path=Path(workspace_path),
                        run_config=_integration_test_runner.FailTestCase(
                            name=name,
                            error_message=error_message,
                        ),
                    )
                )

            case _:
                raise ValueError(
                    "Unknown tets case configuration:\n{}".format(
                        json.dumps(raw_info, indent=4)
                    )
                )

    return test_cases_info
