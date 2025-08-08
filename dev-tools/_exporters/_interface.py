from dataclasses import dataclass
from typing import Any, NewType, Protocol
from pathlib import Path


ExportedWorkspace = NewType("ExportedWorkspace", dict[str, Any])


@dataclass(frozen=True, slots=True)
class ExportFailure:
    exit_code: int
    stdout: str
    stderr: str


type ExportResult = ExportedWorkspace | ExportFailure


class StructurizrWorkspaceExporter(Protocol):
    def export_to_json(self, workspace_path: Path) -> ExportResult: ...
