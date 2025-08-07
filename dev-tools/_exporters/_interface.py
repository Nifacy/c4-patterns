from typing import Any, Protocol
from pathlib import Path


type ExportedWorkspace = dict[str, Any]


class StructurizrWorkspaceExporter(Protocol):
    def export_to_json(self, workspace_path: Path) -> ExportedWorkspace: ...
