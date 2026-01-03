from pathlib import Path
import pytest

def pytest_addoption(parser: pytest.Parser):
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
