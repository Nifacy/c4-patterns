import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Final, Iterable, Mapping
import os

from ._interface import ExportedWorkspace
from ._interface import ExportResult
from ._interface import ExportFailure
from ._interface import StructurizrWorkspaceExporter


class StructurizrCliProcessError(Exception):
    def __init__(self, command: Iterable[str], exit_code: int, stdout: str, stderr: str) -> None:
        self.command = command
        self.exit_code = exit_code
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self) -> str:
        return f"Structurizr CLI command {self.command} returned non-zero exit status {self.exit_code}\nStdout:\n{self.stdout}\nStderr:\n{self.stderr}"


def _run_export_command(
    structurizr_cli_dir: Path,
    workspace_path: Path,
    output_dir: Path,
    *,
    env: Mapping[str, str] | None = None,
) -> ExportResult:
    executable_name = "structurizr.bat" if sys.platform == "win32" else "structurizr.sh"
    executable_path = structurizr_cli_dir / executable_name

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
        env=env or os.environ,
        encoding="utf-8",
        errors="replace",
    )

    try:
        process.check_returncode()
    except subprocess.SubprocessError:
        if process.returncode == 1:
            return ExportFailure(process.stderr)

        raise StructurizrCliProcessError(
            command=command,
            exit_code=process.returncode,
            stdout=process.stdout,
            stderr=process.stderr,
        )

    workspace_name = workspace_path.name.removesuffix(workspace_path.suffix)
    converted_workspace_path = output_dir / f"{workspace_name}.json"

    return ExportedWorkspace(json.loads(converted_workspace_path.read_text()))



class StructurizrCliForLiteVersion(StructurizrWorkspaceExporter):
    _OUTPUT_DIR: Final = "output"

    def __init__(
        self,
        structurizr_cli_dir: Path,
        java_path: Path,
        syntax_plugin_path: Path,
        jweaver_path: Path,
    ):
        self.__structurizr_cli_dir = structurizr_cli_dir
        self.__java_path = java_path
        self.__syntax_plugin_path = syntax_plugin_path
        self.__jweaver_path = jweaver_path

    def export_to_json(self, workspace_path: Path) -> ExportResult:
        output_dir = (self.__structurizr_cli_dir / self._OUTPUT_DIR).absolute()

        shutil.copy(
            self.__syntax_plugin_path,
            self.__structurizr_cli_dir / "lib" / self.__syntax_plugin_path.name,
        )

        return _run_export_command(
            structurizr_cli_dir=self.__structurizr_cli_dir,
            workspace_path=workspace_path,
            output_dir=output_dir,
            env={
                "PATH": f"{os.environ['PATH']}:{self.__java_path.absolute()}",
                "JAVA_TOOL_OPTIONS": f"-javaagent:{self.__jweaver_path.absolute()}",
            },
        )

    def close(self) -> None:
        pass



class StructurizrCliForStandaloneVersion(StructurizrWorkspaceExporter):
    _OUTPUT_DIR: Final = "output"

    def __init__(
        self,
        structurizr_cli_dir: Path,
        java_path: Path,
        syntax_plugin_path: Path,
    ):
        self.__structurizr_cli_dir = structurizr_cli_dir
        self.__java_path = java_path
        self.__syntax_plugin_path = syntax_plugin_path

    def export_to_json(self, workspace_path: Path) -> ExportResult:
        return _run_export_command(
            structurizr_cli_dir=self.__structurizr_cli_dir,
            workspace_path=workspace_path,
            output_dir=(self.__structurizr_cli_dir / self._OUTPUT_DIR).absolute(),
            env={
                "PATH": f"{os.environ['PATH']}:{self.__java_path.absolute()}",
                "JAVA_TOOL_OPTIONS": f"-javaagent:{self.__syntax_plugin_path.absolute()}",
            },
        )

    def close(self) -> None:
        pass
