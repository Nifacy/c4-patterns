import json
from pathlib import Path
import subprocess
import sys
from typing import Final

from ._interface import ExportedWorkspace
from ._interface import ExportResult
from ._interface import ExportFailure
from ._interface import StructurizrWorkspaceExporter


class StructurizrCli(StructurizrWorkspaceExporter):
    _EXEC_NAME: Final = (
        "structurizr.bat" if sys.platform == "win32" else "structurizr.sh"
    )
    _OUTPUT_DIR: Final = "output"

    def __init__(
        self, structurizr_cli_dir: Path, java_path: Path, syntax_plugin_path: Path
    ):
        self.__structurizr_cli_dir = structurizr_cli_dir
        self.__java_path = java_path
        self.__syntax_plugin_path = syntax_plugin_path

    def export_to_json(self, workspace_path: Path) -> ExportResult:
        executable_path = (self.__structurizr_cli_dir / self._EXEC_NAME).absolute()
        output_dir = (self.__structurizr_cli_dir / self._OUTPUT_DIR).absolute()

        command = [
            str(executable_path),
            "export",
            "--format",
            "json",
            "--output",
            str(output_dir),
            "--workspace",
            str(workspace_path.absolute()),
        ]

        process = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env={
                "PATH": str(self.__java_path.absolute()),
                "JAVA_TOOL_OPTIONS": f"-javaagent:{self.__syntax_plugin_path.absolute()}",
            },
        )

        try:
            process.check_returncode()
        except subprocess.SubprocessError:
            return ExportFailure(
                exit_code=process.returncode,
                stdout=process.stdout.decode(errors="replace"),
                stderr=process.stderr.decode(errors="replace"),
            )

        workspace_name = workspace_path.name.removesuffix(workspace_path.suffix)
        converted_workspace_path = output_dir / f"{workspace_name}.json"

        return ExportedWorkspace(json.loads(converted_workspace_path.read_text()))

    def close(self) -> None:
        pass
