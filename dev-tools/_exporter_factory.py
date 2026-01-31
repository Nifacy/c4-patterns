import dataclasses
import shutil
import stat
import sys
from typing import Final, Protocol
import zipfile

import _exporters
from _cached_downloader import CachedDownloader
import _logging_tools
import _exporter_release

from pathlib import Path
import logging


_STRUCTURIZR_CLI_ARCHIVE_NAME: Final = "structurizr-cli.zip"
_STRUCTURIZR_CLI_DIR: Final = "structurizr-cli"
_STRUCTURIZR_CLI_SHELL_FILE: Final = "structurizr.sh"
_JWEAVER_NAME: Final = "aspectjweaver.jar"


class ExporterFactory(Protocol):
    def __call__(self, java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrWorkspaceExporter:
        ...


@dataclasses.dataclass(frozen=True, slots=True)
class JWeaverRelease:
    url: str
    version: str


@dataclasses.dataclass(frozen=True, slots=True)
class _ExporterConfigBase:
    exporter_release: _exporter_release.ExporterRelease


@dataclasses.dataclass(frozen=True, slots=True)
class LiteVersionExporterConfig(_ExporterConfigBase):
    jweaver_release: JWeaverRelease


@dataclasses.dataclass(frozen=True, slots=True)
class StandaloneVersionExporterConfig(_ExporterConfigBase):
    pass


type ExporterConfig = LiteVersionExporterConfig | StandaloneVersionExporterConfig


def _prepare_structurizr_cli_environment(downloader: CachedDownloader, release: _exporter_release.StructurizrCliRelease, temp_dir_path: Path, log: logging.Logger) -> Path:
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

    return structurizr_cli_dir


def _prepare_structurizr_lite_environment(
    downloader: CachedDownloader,
    release: _exporter_release.StructurizrLiteRelease,
    temp_dir_path: Path,
    log: logging.Logger,
) -> Path:
    structurizr_lite_dir = temp_dir_path / "structurizr-lite"
    structurizr_lite_war_file = structurizr_lite_dir / "structurizr-lite.war"

    structurizr_lite_dir.mkdir()

    with _logging_tools.log_action(log, "Install structurizr lite"):
        downloader.install_file(
            url=release.url,
            output_path=structurizr_lite_war_file,
        )

    return structurizr_lite_dir


def _install_jweaver(downloader: CachedDownloader, temp_dir_path: Path, release: JWeaverRelease, log: logging.Logger) -> Path:
    aspect_jweaver_path = temp_dir_path / _JWEAVER_NAME

    with _logging_tools.log_action(log, "Install jweaver"):
        downloader.install_file(
            url=release.url,
            output_path=aspect_jweaver_path,
        )

    return aspect_jweaver_path


def _get_structurizr_cli_lite_exporter_factory(
    downloader: CachedDownloader,
    jweaver_release: JWeaverRelease,
    release: _exporter_release.StructurizrCliRelease,
    temp_dir_path: Path,
    log: logging.Logger,
) -> ExporterFactory:
    structurizr_cli_dir = _prepare_structurizr_cli_environment(
        downloader=downloader,
        release=release,
        temp_dir_path=temp_dir_path,
        log=log,
    )

    jweaver_path = _install_jweaver(
        downloader=downloader,
        temp_dir_path=temp_dir_path,
        release=jweaver_release,
        log=log,
    )

    def _create_structurizr_cli_exporter(java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrCliForLiteVersion:
        return _exporters.StructurizrCliForLiteVersion(
            structurizr_cli_dir=structurizr_cli_dir,
            java_path=java_path,
            syntax_plugin_path=syntax_plugin_path,
            jweaver_path=jweaver_path,
        )

    return _create_structurizr_cli_exporter


def _get_structurizr_cli_standalone_exporter_factory(
    downloader: CachedDownloader,
    release: _exporter_release.StructurizrCliRelease,
    temp_dir_path: Path,
    log: logging.Logger,
) -> ExporterFactory:
    structurizr_cli_dir = _prepare_structurizr_cli_environment(
        downloader=downloader,
        release=release,
        temp_dir_path=temp_dir_path,
        log=log,
    )

    def _create_structurizr_cli_exporter(java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrCliForStandaloneVersion:
        return _exporters.StructurizrCliForStandaloneVersion(
            structurizr_cli_dir=structurizr_cli_dir,
            java_path=java_path,
            syntax_plugin_path=syntax_plugin_path,
        )

    return _create_structurizr_cli_exporter


def _get_structurizr_lite_lite_exporter_factory(
    downloader: CachedDownloader,
    jweaver_release: JWeaverRelease,
    release: _exporter_release.StructurizrLiteRelease,
    temp_dir_path: Path,
    log: logging.Logger,
) -> ExporterFactory:
    structurizr_lite_dir = _prepare_structurizr_lite_environment(
        downloader=downloader,
        release=release,
        temp_dir_path=temp_dir_path,
        log=log,
    )

    jweaver_path = _install_jweaver(
        downloader=downloader,
        temp_dir_path=temp_dir_path,
        release=jweaver_release,
        log=log,
    )

    def _create_exporter(java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrLiteForLiteVersion:
        return _exporters.StructurizrLiteForLiteVersion(
            structurizr_lite_dir=structurizr_lite_dir,
            java_path=java_path,
            syntax_plugin_path=syntax_plugin_path,
            stdout_path=temp_dir_path / "stdout.txt",
            stderr_path=temp_dir_path / "stderr.txt",
            log=log,
            jweaver_path=jweaver_path,
        )

    return _create_exporter

def _get_structurizr_lite_standalone_exporter_factory(
    downloader: CachedDownloader,
    release: _exporter_release.StructurizrLiteRelease,
    temp_dir_path: Path,
    log: logging.Logger,
) -> ExporterFactory:
    structurizr_lite_dir = _prepare_structurizr_lite_environment(
        downloader=downloader,
        release=release,
        temp_dir_path=temp_dir_path,
        log=log,
    )

    def _create_exporter(java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrLiteForStandaloneVersion:
        return _exporters.StructurizrLiteForStandaloneVersion(
            structurizr_lite_dir=structurizr_lite_dir,
            java_path=java_path,
            syntax_plugin_path=syntax_plugin_path,
            stdout_path=temp_dir_path / "stdout.txt",
            stderr_path=temp_dir_path / "stderr.txt",
            log=log,
        )

    return _create_exporter

def get_exporter_factory(downloader: CachedDownloader, config: ExporterConfig, temp_dir_path: Path, log: logging.Logger) -> ExporterFactory:
    match config:
        case LiteVersionExporterConfig(exporter_release=_exporter_release.StructurizrCliRelease()):
            return _get_structurizr_cli_lite_exporter_factory(
                downloader=downloader,
                jweaver_release=config.jweaver_release,
                release=config.exporter_release,
                temp_dir_path=temp_dir_path,
                log=log,
            )
        case LiteVersionExporterConfig(exporter_release=_exporter_release.StructurizrLiteRelease()):
            return _get_structurizr_lite_lite_exporter_factory(
                downloader=downloader,
                jweaver_release=config.jweaver_release,
                release=config.exporter_release,
                temp_dir_path=temp_dir_path,
                log=log,
            )
        case StandaloneVersionExporterConfig(exporter_release=_exporter_release.StructurizrCliRelease()):
            return _get_structurizr_cli_standalone_exporter_factory(
                downloader=downloader,
                release=config.exporter_release,
                temp_dir_path=temp_dir_path,
                log=log,
            )
        case StandaloneVersionExporterConfig(exporter_release=_exporter_release.StructurizrLiteRelease()):
            return _get_structurizr_lite_standalone_exporter_factory(
                downloader=downloader,
                release=config.exporter_release,
                temp_dir_path=temp_dir_path,
                log=log,
            )
