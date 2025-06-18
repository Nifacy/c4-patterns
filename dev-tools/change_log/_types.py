from dataclasses import dataclass


@dataclass
class IssueInfo:
    number: int
    link: str


@dataclass
class ChangeItem:
    description: str
    issue_info: IssueInfo


@dataclass
class VersionChanges:
    version: str
    external: list[ChangeItem]
    internal: list[ChangeItem]


@dataclass
class ChangeLog:
    version_changes: list[VersionChanges]
