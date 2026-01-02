from pathlib import Path
import pytest

import _release_extractor
import _test_case_info_extractor


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--test-case-config",
        type=Path,
        required=True,
        help="Path to test case configuration file",
    )

    parser.addoption(
        "--env-config",
        type=Path,
        required=True,
        help="Path to test environment configuration file",
    )

    parser.addoption(
        "--plugin-path",
        type=Path,
        required=True,
        help="Path to pattern-syntax-plugin JAR archive",
    )

    parser.addoption(
        "--java-path",
        type=Path,
        required=True,
        help="Path to java binary directory",
    )

    parser.addoption(
        "--samples-dir",
        type=Path,
        required=True,
        help="Path to a directory with Structurizr workspace test samples",
    )


def pytest_generate_tests(metafunc: pytest.Metafunc) -> None:
    if "exporter_release" in metafunc.fixturenames:
        env_config_file_path = metafunc.config.getoption("--env-config")
        exporter_releases = _release_extractor.extract_exporter_releases_from_file(env_config_file_path)
        param_ids = [str(exporter_release) for exporter_release in exporter_releases]
        metafunc.parametrize("exporter_release", exporter_releases, ids=param_ids)

    if "test_case_info" in metafunc.fixturenames:
        test_case_config_file_path = metafunc.config.getoption("--test-case-config")
        test_cases_info = _test_case_info_extractor.extract_test_cases_info_from_file(
            test_case_config_file_path
        )
        param_ids = [test_case_info.name for test_case_info in test_cases_info]
        metafunc.parametrize("test_case_info", test_cases_info, ids=param_ids)
