from pathlib import Path
from typing import Any

import pytest


class _ExistingPath(Path):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)

        if not self.exists():
            raise ValueError(f"Path '{self}' not exists")


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--plugin-path",
        type=_ExistingPath,
        required=True,
        help="Path to pattern-syntax-plugin JAR archive",
    )

    parser.addoption(
        "--java-path",
        type=_ExistingPath,
        required=True,
        help="Path to java binary directory",
    )

    parser.addoption(
        "--samples-dir",
        type=_ExistingPath,
        required=True,
        help="Path to a directory with Structurizr workspace test samples",
    )


@pytest.fixture
def syntax_plugin_path(request: pytest.FixtureRequest) -> Path:
    return request.config.getoption('--plugin-path')


@pytest.fixture
def java_path(request: pytest.FixtureRequest) -> Path:
    return request.config.getoption('--java-path')


@pytest.fixture
def samples_dir_path(request: pytest.FixtureRequest) -> Path:
    return request.config.getoption("--samples-dir")
