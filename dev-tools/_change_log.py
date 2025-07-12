from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Change:
    description: str
    link: str


@dataclass(frozen=True, slots=True)
class VersionChanges:
    version: str
    external_changes: tuple[Change, ...]
    internal_changes: tuple[Change, ...]


@dataclass(frozen=True, slots=True)
class ChangeLog:
    version_changes: tuple[VersionChanges, ...]


def create_empty_log() -> ChangeLog:
    return ChangeLog(version_changes=tuple())


def add_version(change_log: ChangeLog, version: str) -> ChangeLog:
    new_version = VersionChanges(
        version=version,
        external_changes=tuple(),
        internal_changes=tuple(),
    )
    updated_version_changes = change_log.version_changes + (new_version,)
    return ChangeLog(version_changes=updated_version_changes)


def add_external_change(change_log: ChangeLog, change: Change) -> ChangeLog:
    *versions, last_version = change_log.version_changes
    updated_last_version = VersionChanges(
        version=last_version.version,
        external_changes=last_version.external_changes + (change,),
        internal_changes=last_version.internal_changes,
    )

    return ChangeLog(version_changes=tuple(versions) + (updated_last_version,))


def add_internal_change(change_log: ChangeLog, change: Change) -> ChangeLog:
    *versions, last_version = change_log.version_changes
    updated_last_version = VersionChanges(
        version=last_version.version,
        external_changes=last_version.external_changes,
        internal_changes=last_version.internal_changes + (change,),
    )

    return ChangeLog(version_changes=tuple(versions) + (updated_last_version,))
