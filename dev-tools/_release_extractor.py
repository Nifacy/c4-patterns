import dataclasses
import json
from pathlib import Path
from typing import Any


@dataclasses.dataclass(frozen=True, slots=True)
class StructurizrCliRelease:
    version: str
    url: str

    def __str__(self) -> str:
        return f"StructurizrCli(version={self.version})"


@dataclasses.dataclass(frozen=True, slots=True)
class StructurizrLiteRelease:
    version: str
    url: str

    def __str__(self) -> str:
        return f"StructurizrLite(version={self.version})"


type ExporterRelease = StructurizrCliRelease | StructurizrLiteRelease


def _get_exporter_release(raw_release: Any) -> ExporterRelease | None:
    match raw_release:
        case {"type": "structurizr-cli", "version": str(version), "url": str(url)}:
            return StructurizrCliRelease(
                version=version,
                url=url,
            )
        case {"type": "structurizr-lite", "version": str(version), "url": str(url)}:
            return StructurizrLiteRelease(
                version=version,
                url=url,
            )
        case _:
            return None


def extract_exporter_releases_from_file(config_file: Path) -> list[ExporterRelease]:
    raw_data = json.loads(config_file.read_text())
    releases: list[ExporterRelease] = []

    match raw_data:
        case [*raw_releases]:
            for raw_release in raw_releases:
                release = _get_exporter_release(raw_release)
                if release is not None:
                    releases.append(release)
                else:
                    raise ValueError("Unknown release configuration:\n{}".format(json.dumps(raw_release, indent=4)))
        case _:
            raise ValueError("Unknown releases configuration:\n{}".format(json.dumps(raw_data, indent=4)))

    return releases
