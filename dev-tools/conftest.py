from pathlib import Path
import pytest


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
