import logging
from pathlib import Path
import tempfile
from typing import Final
import pytest
import _exporter_factory
import _integration_test_runner
import _logging_tools
import _release_extractor
import _test_case_info_extractor
import _cached_downloader


_CUR_DIR_PATH: Final = Path(__file__).parent
_DOWNLOAD_CACHE_PATH: Final = _CUR_DIR_PATH / ".." / ".cache"


@pytest.fixture
def test_case_config_file(request: pytest.FixtureRequest) -> Path:
    return request.config.getoption('--test-case-config')


@pytest.fixture
def syntax_plugin_path(request: pytest.FixtureRequest) -> Path:
    return request.config.getoption('--plugin-path')


@pytest.fixture
def java_path(request: pytest.FixtureRequest) -> Path:
    return request.config.getoption('--java-path')


def test_syntax_plugin(exporter_release: _release_extractor.ExporterRelease, test_case_config_file: Path, syntax_plugin_path: Path, java_path: Path) -> None:
    log = logging.getLogger()
    downloader = _cached_downloader.CachedDownloader(log, _DOWNLOAD_CACHE_PATH)

    with _logging_tools.log_action(log, "Extract test case configuration"):
        test_cases_info = _test_case_info_extractor.extract_test_cases_info_from_file(
            test_case_config_file
        )

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir_path = Path(temp_dir)

        with _logging_tools.log_action(log, "Test pattern-syntax-plugin work in specified environment"):
            log.debug(
                "Context:\n"
                f"- Exporter: {exporter_release}\n"
            )

            exporter_factory = _exporter_factory.get_exporter_factory(downloader, exporter_release, temp_dir_path, log)

            with _logging_tools.log_action(log, "Run integration tests"):
                for test_case_info in test_cases_info:
                    log.info(f"Run '{test_case_info.name}' test case ...")

                    exporter = exporter_factory(
                        java_path=java_path,
                        syntax_plugin_path=syntax_plugin_path,
                    )

                    try:
                        _integration_test_runner.run_integration_test_case(
                            run_config=test_case_info.run_config,
                            exporter=exporter,
                            workspace_path=test_case_info.workspace_path,
                        )
                    finally:
                        exporter.close()

                    log.info(f"Run '{test_case_info.name}' test case ... ok")
