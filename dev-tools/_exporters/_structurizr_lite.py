import json
import subprocess

import requests
from ._interface import StructurizrWorkspaceExporter
from ._interface import ExportResult
from ._interface import ExportedWorkspace
from ._interface import ExportFailure

from pathlib import Path

import shutil


class StructurizrLite(StructurizrWorkspaceExporter):
    def __init__(self, structurizr_lite_dir: Path, java_path: Path, syntax_plugin_path: Path):
        self.__structurizr_lite_dir = structurizr_lite_dir
        self.__java_path = java_path
        self.__syntax_plugin_path = syntax_plugin_path

        self.__structurizr_lite_jar = self.__structurizr_lite_dir / "structurizr-lite.war"
        if not self.__structurizr_lite_jar.exists():
            raise FileNotFoundError(f"Structurizr Lite JAR not found at {self.__structurizr_lite_jar}")

    def export_to_json(self, workspace_path: Path) -> ExportResult:
        workspace_dir = self.__structurizr_lite_dir / ".workspace"
        shutil.copytree(workspace_path.parent, workspace_dir)

        try:
            command = [
                "java",
                f"-javaagent:{self.__syntax_plugin_path}",
                "-jar",
                str(self.__structurizr_lite_jar),
                str(workspace_dir),
            ]

            process = subprocess.Popen(
                command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env={
                    "PATH": str(self.__java_path.absolute()),
                    "STRUCTURIZR_WORKSPACE_FILENAME": workspace_path.stem,
                }
            )
            assert process.stdout is not None
            assert process.stderr is not None

            response = requests.get("http://localhost:8080/")
            if response.status_code != 200:
                process.kill()
                return ExportFailure(
                    exit_code=process.wait(),
                    stdout=process.stdout.read().decode(errors="replace"),
                    stderr=process.stderr.read().decode(errors="replace"),
                )

            output_file = workspace_dir / (workspace_path.stem + ".json")
            if not output_file.exists():
                raise FileNotFoundError(f"Expected output file not found at {output_file}")

            return ExportedWorkspace(json.loads(output_file.read_text(encoding="utf-8")))
        finally:
            shutil.rmtree(workspace_dir)
