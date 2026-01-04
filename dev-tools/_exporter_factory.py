import stat
import sys
from typing import Final, Protocol
import zipfile

import _exporters
from _cached_downloader import CachedDownloader
import _logging_tools
import _release_extractor

from pathlib import Path
import logging


_STRUCTURIZR_CLI_ARCHIVE_NAME: Final = "structurizr-cli.zip"
_STRUCTURIZR_CLI_DIR: Final = "structurizr-cli"
_STRUCTURIZR_CLI_SHELL_FILE: Final = "structurizr.sh"


class ExporterFactory(Protocol):
    def __call__(self, java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrWorkspaceExporter:
        ...


def _get_structurizr_cli_exporter_factory(downloader: CachedDownloader, release: _release_extractor.StructurizrCliRelease, temp_dir_path: Path, log: logging.Logger) -> ExporterFactory:
    structurizr_archive_path = temp_dir_path / _STRUCTURIZR_CLI_ARCHIVE_NAME
    structurizr_cli_dir = temp_dir_path / _STRUCTURIZR_CLI_DIR

    with _logging_tools.log_action(log, "Install structurizr cli"):
        downloader.install_file(
            url=release.url,
            output_path=structurizr_archive_path,
        )

    with _logging_tools.log_action(log, "Extract structurizr cli"):
        with zipfile.ZipFile(structurizr_archive_path) as archive:
            archive.extractall(structurizr_cli_dir)

    if sys.platform != "win32":
        script_path = structurizr_cli_dir / _STRUCTURIZR_CLI_SHELL_FILE
        current_permissions = script_path.stat().st_mode
        script_path.chmod(current_permissions | stat.S_IXUSR)

    def _create_structurizr_cli_exporter(java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrCli:
        return _exporters.StructurizrCli(
            structurizr_cli_dir=structurizr_cli_dir,
            java_path=java_path,
            syntax_plugin_path=syntax_plugin_path,
        )

    return _create_structurizr_cli_exporter


def _get_structurizr_lite_exporter_factory(downloader: CachedDownloader, release: _release_extractor.StructurizrLiteRelease, temp_dir_path: Path, log: logging.Logger) -> ExporterFactory:
    structurizr_lite_dir = temp_dir_path / "structurizr-lite"
    structurizr_lite_dir.mkdir()

    structurizr_lite_war_file = structurizr_lite_dir / "structurizr-lite.war"

    with _logging_tools.log_action(log, "Install structurizr lite"):
        downloader.install_file(
            url=release.url,
            output_path=structurizr_lite_war_file,
        )

    def _create_structurizr_lite_exporter(java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrLite:
        return _exporters.StructurizrLite(
            structurizr_lite_dir=structurizr_lite_dir,
            java_path=java_path,
            syntax_plugin_path=syntax_plugin_path,
            stdout_path=temp_dir_path / "stdout.txt",
            stderr_path=temp_dir_path / "stderr.txt",
        )

    return _create_structurizr_lite_exporter


def get_exporter_factory(downloader: CachedDownloader, release: _release_extractor.ExporterRelease, temp_dir_path: Path, log: logging.Logger) -> ExporterFactory:
    match release:
        case _release_extractor.StructurizrCliRelease() as cli_release:
            return _get_structurizr_cli_exporter_factory(downloader, cli_release, temp_dir_path, log)
        case _release_extractor.StructurizrLiteRelease() as lite_release:
            return _get_structurizr_lite_exporter_factory(downloader, lite_release, temp_dir_path, log)
