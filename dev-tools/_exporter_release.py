import dataclasses


@dataclasses.dataclass(frozen=True, slots=True)
class StructurizrCliRelease:
    version: str
    url: str

    def __str__(self) -> str:
        return f"StructurizrCli(version='{self.version}')"


@dataclasses.dataclass(frozen=True, slots=True)
class StructurizrLiteRelease:
    version: str
    url: str

    def __str__(self) -> str:
        return f"StructurizrLite(version='{self.version}')"


type ExporterRelease = StructurizrCliRelease | StructurizrLiteRelease
