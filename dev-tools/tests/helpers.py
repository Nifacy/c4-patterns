from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class PatternSyntaxPluginDistributive:
    lite_version: Path
    standalone_version: Path

    @classmethod
    def from_dist_directory(cls, directory: Path) -> PatternSyntaxPluginDistributive:
        return PatternSyntaxPluginDistributive(
            lite_version=cls.__validate_path(directory / "lite.jar"),
            standalone_version=cls.__validate_path(directory / "standalone.jar"),
        )     

    @staticmethod
    def __validate_path(path: Path) -> Path:
        if not path.exists():
            raise ValueError(f"Path '{path.absolute()}' not exists")

        return path
