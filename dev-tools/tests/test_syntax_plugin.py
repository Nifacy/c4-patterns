import contextlib
import dataclasses
import json
import logging
from pathlib import Path
import tempfile
from typing import Final, Iterable, Iterator, assert_never
import pytest
import _exporter_factory
import _exporters
import _logging_tools
import _exporter_release
import _cached_downloader

from .helpers import PatternSyntaxPluginDistributive


_CUR_DIR_PATH: Final = Path(__file__).parent
_DOWNLOAD_CACHE_PATH: Final = _CUR_DIR_PATH / ".." / ".cache"
_JWEAVER_RELEASES: Final = (
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.0/aspectjweaver-1.9.0.jar",
        version="1.9.0",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.1/aspectjweaver-1.9.1.jar",
        version="1.9.1",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.2/aspectjweaver-1.9.2.jar",
        version="1.9.2",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.3/aspectjweaver-1.9.3.jar",
        version="1.9.3",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.4/aspectjweaver-1.9.4.jar",
        version="1.9.4",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.5/aspectjweaver-1.9.5.jar",
        version="1.9.5",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.6/aspectjweaver-1.9.6.jar",
        version="1.9.6",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.7/aspectjweaver-1.9.7.jar",
        version="1.9.7",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.8/aspectjweaver-1.9.8.jar",
        version="1.9.8",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.9/aspectjweaver-1.9.9.jar",
        version="1.9.9",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.19/aspectjweaver-1.9.19.jar",
        version="1.9.19",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.20/aspectjweaver-1.9.20.jar",
        version="1.9.20",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.21/aspectjweaver-1.9.21.jar",
        version="1.9.21",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.22/aspectjweaver-1.9.22.jar",
        version="1.9.22",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.23/aspectjweaver-1.9.23.jar",
        version="1.9.23",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.24/aspectjweaver-1.9.24.jar",
        version="1.9.24",
    ),
    _exporter_factory.JWeaverRelease(
        url="https://repo1.maven.org/maven2/org/aspectj/aspectjweaver/1.9.25/aspectjweaver-1.9.25.jar",
        version="1.9.25",
    ),
)

@dataclasses.dataclass(frozen=True, slots=True)
class SuccessTestResult:
    expected_result_path: Path


@dataclasses.dataclass(frozen=True, slots=True)
class FailedTestResult:
    error_message: str


@dataclasses.dataclass(frozen=True, slots=True)
class TestConfiguration:
    name: str
    exporter_config: _exporter_factory.ExporterConfig
    result: SuccessTestResult | FailedTestResult
    workspace_path: Path

    @property
    def param_id(self) -> str:
        config_params = {
            "release": self.exporter_config.exporter_release.version,
            "test_case": self.name,
        }

        match self.exporter_config:
            case _exporter_factory.LiteVersionExporterConfig():
                config_params["plugin_version"] = "lite"
                config_params["jweaver"] = self.exporter_config.jweaver_release.version
            case _exporter_factory.StandaloneVersionExporterConfig():
                config_params["plugin_version"] = "standalone"

        match self.exporter_config.exporter_release:
            case _exporter_release.StructurizrCliRelease():
                config_params["exporter_type"] = "structurizr_cli"
            case _exporter_release.StructurizrLiteRelease():
                config_params["exporter_type"] = "structurizr_lite"

        return " ".join(f"{key}:{value}" for key, value in config_params.items())

@dataclasses.dataclass(frozen=True, slots=True)
class ReducedTestConfiguration:
    name: str
    result: SuccessTestResult | FailedTestResult
    workspace_path: Path


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


def _get_test_configs(
    releases: Iterable[_exporter_release.ExporterRelease],
    reduced_test_configs: Iterable[ReducedTestConfiguration],
) -> list[TestConfiguration]:
    return [
        TestConfiguration(
            name=reduced_test_config.name,
            exporter_config=_exporter_factory.StandaloneVersionExporterConfig(release) if jweaver_release is None else _exporter_factory.LiteVersionExporterConfig(release, jweaver_release),
            result=reduced_test_config.result,
            workspace_path=reduced_test_config.workspace_path,
        )
        for release in releases
        for reduced_test_config in reduced_test_configs
        for jweaver_release in (*_JWEAVER_RELEASES, None)
    ]


@pytest.mark.parametrize(
    "test_config",
    [
        *_get_test_configs(
            releases=[
                _exporter_release.StructurizrCliRelease(
                    version="v2025.03.28",
                    url="https://github.com/structurizr/cli/releases/download/v2025.03.28/structurizr-cli.zip",
                ),
                _exporter_release.StructurizrCliRelease(
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
                _exporter_release.StructurizrLiteRelease(
                    version="v2025.03.28",
                    url="https://github.com/structurizr/lite/releases/download/v2025.03.28/structurizr-lite.war",
                ),
                _exporter_release.StructurizrLiteRelease(
                    version="v2025.05.28",
                    url="https://github.com/structurizr/lite/releases/download/v2025.05.28/structurizr-lite.war",
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
    syntax_plugin_dist: PatternSyntaxPluginDistributive,
    java_path: Path,
    samples_dir_path: Path,
    datadir: Path,
) -> None:
    log = logging.getLogger()
    downloader = _cached_downloader.CachedDownloader(log, _DOWNLOAD_CACHE_PATH)
    workspace_path = samples_dir_path / test_config.workspace_path

    match test_config.exporter_config:
        case _exporter_factory.LiteVersionExporterConfig():
            syntax_plugin_path = syntax_plugin_dist.lite_version
        case _exporter_factory.StandaloneVersionExporterConfig():
            syntax_plugin_path = syntax_plugin_dist.standalone_version
        case _:
            raise assert_never(test_config.exporter_config)

    with tempfile.TemporaryDirectory() as temp_dir:
        exporter_factory = _exporter_factory.get_exporter_factory(downloader, test_config.exporter_config, Path(temp_dir), log)

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
