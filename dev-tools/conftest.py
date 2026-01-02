from pathlib import Path
import pytest

import _release_extractor


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


def pytest_generate_tests(metafunc: pytest.Metafunc):
    if "exporter_release" in metafunc.fixturenames:
        env_config_file = metafunc.config.getoption("--env-config")
        exporter_releases = _release_extractor.extract_exporter_releases_from_file(env_config_file)
        param_ids = [str(exporter_release) for exporter_release in exporter_releases]
        metafunc.parametrize("exporter_release", exporter_releases, ids=param_ids)
