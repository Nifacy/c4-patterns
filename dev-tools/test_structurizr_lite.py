import logging
import os
from pathlib import Path
import tempfile
from typing import Final

import _exporter_factory
import _cached_downloader
import _release_extractor


CUR_DIR_PATH: Final = Path(__file__).parent
SYNTAX_PLUGIN_PATH: Final = CUR_DIR_PATH / "temp" / "pattern-syntax-plugin-1.0.jar"
JAVA_BINARY_DIR_PATH = Path(os.environ["JAVA_HOME"]) / "bin"
WORKSPACE_PATH: Final = CUR_DIR_PATH / "temp" / "samples" / "layered.dsl"

log = logging.getLogger()
log.setLevel(logging.DEBUG)

downloader = _cached_downloader.CachedDownloader(
    log=log,
    cache_path=Path(".cache"),
)

with tempfile.TemporaryDirectory() as temp_dir:
    exporter_factory = _exporter_factory.get_exporter_factory(
        downloader=downloader,
        release=_release_extractor.StructurizrLiteRelease(
            version="v2025.03.28",
            url="https://github.com/structurizr/lite/releases/download/v2025.03.28/structurizr-lite.war",
        ),
        temp_dir_path=Path(temp_dir),
        log=log,
    )

    exporter = exporter_factory(
        java_path=JAVA_BINARY_DIR_PATH,
        syntax_plugin_path=SYNTAX_PLUGIN_PATH,
    )

    try:
        result = exporter.export_to_json(WORKSPACE_PATH)
        print(f"Export result: {result}")
    finally:
        exporter.close()


with tempfile.TemporaryDirectory() as temp_dir:
    exporter_factory = _exporter_factory.get_exporter_factory(
        downloader=downloader,
        release=_release_extractor.StructurizrCliRelease(
            version="v2025.05.28",
            url="https://github.com/structurizr/cli/releases/download/v2025.05.28/structurizr-cli.zip",
        ),
        temp_dir_path=Path(temp_dir),
        log=log,
    )

    exporter = exporter_factory(
        java_path=JAVA_BINARY_DIR_PATH,
        syntax_plugin_path=SYNTAX_PLUGIN_PATH,
    )

    try:
        result = exporter.export_to_json(WORKSPACE_PATH)
        print(f"Export result: {result}")
    finally:
        exporter.close()
