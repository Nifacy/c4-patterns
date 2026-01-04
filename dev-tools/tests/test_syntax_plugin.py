import contextlib
import dataclasses
import json
import logging
from pathlib import Path
import tempfile
from typing import Final, Iterable, Iterator
import pytest
import _exporter_factory
import _exporters
import _logging_tools
import _release_extractor
import _cached_downloader


_CUR_DIR_PATH: Final = Path(__file__).parent
_DOWNLOAD_CACHE_PATH: Final = _CUR_DIR_PATH / ".." / ".cache"

@dataclasses.dataclass(frozen=True, slots=True)
class SuccessTestResult:
    expected_result_path: Path


@dataclasses.dataclass(frozen=True, slots=True)
class FailedTestResult:
    error_message: str


@dataclasses.dataclass(frozen=True, slots=True)
class TestConfiguration:
    name: str
    release: _release_extractor.ExporterRelease
    result: SuccessTestResult | FailedTestResult
    workspace_path: Path

    @property
    def param_id(self) -> str:
        return f"release={self.release}, test_case='{self.name}'"


@dataclasses.dataclass(frozen=True, slots=True)
class ReducedTestConfiguration:
    name: str
    result: SuccessTestResult | FailedTestResult
    workspace_path: Path


def _validate_path(path: Path) -> Path:
    path = path.resolve()
    if not path.exists():
        raise ValueError(f"Path '{path.absolute()}' not exists")
    return path


@pytest.fixture
def syntax_plugin_path(request: pytest.FixtureRequest) -> Path:
    return _validate_path(request.config.getoption('--plugin-path'))


@pytest.fixture
def java_path(request: pytest.FixtureRequest) -> Path:
    return _validate_path(request.config.getoption('--java-path'))


@pytest.fixture
def samples_dir_path(request: pytest.FixtureRequest) -> Path:
    return _validate_path(request.config.getoption("--samples-dir"))


@contextlib.contextmanager
def _create_exporter(exporter_factory: _exporter_factory.ExporterFactory, java_path: Path, syntax_plugin_path: Path) -> Iterator[_exporters.StructurizrWorkspaceExporter]:
    exporter = exporter_factory(
        java_path=java_path,
        syntax_plugin_path=syntax_plugin_path,
    )

    try:
        yield exporter
    finally:
        exporter.close()    


def _get_test_configs(releases: Iterable[_release_extractor.ExporterRelease], reduced_test_configs: Iterable[ReducedTestConfiguration]) -> list[TestConfiguration]:
    return [
        TestConfiguration(
            name=reduced_test_config.name,
            release=release,
            result=reduced_test_config.result,
            workspace_path=reduced_test_config.workspace_path,
        )
        for release in releases
        for reduced_test_config in reduced_test_configs
    ]


@pytest.mark.parametrize(
    "test_config",
    [
        *_get_test_configs(
            releases=[
                _release_extractor.StructurizrCliRelease(
                    version="v2025.03.28",
                    url="https://github.com/structurizr/cli/releases/download/v2025.03.28/structurizr-cli.zip",
                ),
                _release_extractor.StructurizrCliRelease(
                    version="v2025.05.28",
                    url="https://github.com/structurizr/cli/releases/download/v2025.05.28/structurizr-cli.zip",
                ),
            ],
            reduced_test_configs=[
                ReducedTestConfiguration(
                    name="database-per-service",
                    workspace_path=Path("databasePerService.dsl"),
                    result=FailedTestResult(
                        error_message="Database 'Payment Service' is already used by 'Order Application'",
                    ),
                ),
                ReducedTestConfiguration(
                    name="layered",
                    workspace_path=Path("layered.dsl"),
                    result=SuccessTestResult(
                        expected_result_path=Path("results/structurizr-cli/layered.json"),
                    ),
                ),
                ReducedTestConfiguration(
                    name="reverse-proxy",
                    workspace_path=Path("reverseProxy.dsl"),
                    result=SuccessTestResult(
                        expected_result_path=Path("results/structurizr-cli/reverseProxy.json"),
                    ),
                ),
                ReducedTestConfiguration(
                    name="saga",
                    workspace_path=Path("saga.dsl"),
                    result=SuccessTestResult(
                        expected_result_path=Path("results/structurizr-cli/saga.json"),
                    ),
                ),
                ReducedTestConfiguration(
                    name="service-registry",
                    workspace_path=Path("serviceRegistry.dsl"),
                    result=SuccessTestResult(
                        expected_result_path=Path("results/structurizr-cli/serviceRegistry.json"),
                    ),
                ),
            ]
        ),
        *_get_test_configs(
            releases=[
                _release_extractor.StructurizrLiteRelease(
                    version="v2025.03.28",
                    url="https://github.com/structurizr/lite/releases/download/v2025.03.28/structurizr-lite.war",
                ),
            ],
            reduced_test_configs=[
                ReducedTestConfiguration(
                    name="database-per-service",
                    workspace_path=Path("databasePerService.dsl"),
                    result=FailedTestResult(
                        error_message="Database 'Payment Service' is already used by 'Order Application'",
                    ),
                ),
                ReducedTestConfiguration(
                    name="layered",
                    workspace_path=Path("layered.dsl"),
                    result=SuccessTestResult(
                        expected_result_path=Path("results/structurizr-lite/layered.json"),
                    ),
                ),
                ReducedTestConfiguration(
                    name="reverse-proxy",
                    workspace_path=Path("reverseProxy.dsl"),
                    result=SuccessTestResult(
                        expected_result_path=Path("results/structurizr-lite/reverseProxy.json"),
                    ),
                ),
                ReducedTestConfiguration(
                    name="saga",
                    workspace_path=Path("saga.dsl"),
                    result=SuccessTestResult(
                        expected_result_path=Path("results/structurizr-lite/saga.json"),
                    ),
                ),
                ReducedTestConfiguration(
                    name="service-registry",
                    workspace_path=Path("serviceRegistry.dsl"),
                    result=SuccessTestResult(
                        expected_result_path=Path("results/structurizr-lite/serviceRegistry.json"),
                    ),
                )
            ]
        ),
    ],
    ids=lambda test_config: test_config.param_id,
)
def test_syntax_plugin(
    test_config: TestConfiguration,
    syntax_plugin_path: Path,
    java_path: Path,
    samples_dir_path: Path,
    datadir: Path,
) -> None:
    log = logging.getLogger()
    downloader = _cached_downloader.CachedDownloader(log, _DOWNLOAD_CACHE_PATH)
    workspace_path = samples_dir_path / test_config.workspace_path

    with tempfile.TemporaryDirectory() as temp_dir:
        exporter_factory = _exporter_factory.get_exporter_factory(downloader, test_config.release, Path(temp_dir), log)

        with _logging_tools.log_action(log, "Run integration test"):
            with _create_exporter(exporter_factory, java_path, syntax_plugin_path) as exporter:
                export_result = exporter.export_to_json(workspace_path)

                match test_config.result:
                    case SuccessTestResult(expected_result_path=expected_result_path):
                        expected_result = json.loads((datadir / expected_result_path).read_text())

                        assert not isinstance(
                            export_result, _exporters.ExportFailure
                        ), "Export result unexpected failed"

                        assert (
                            export_result == expected_result
                        ), "Exported workspace not equals to expected"

                    case FailedTestResult(error_message=error_message):
                        assert isinstance(
                            export_result, _exporters.ExportFailure
                        ), "Export result unexpected success"

                        assert (
                            error_message in export_result.error_message
                        ), "Stderr doesn't contain error message"
