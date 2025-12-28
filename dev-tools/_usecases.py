import contextlib
from dataclasses import dataclass
import itertools
import json
import logging
from pathlib import Path
import tempfile
from typing import Any, Final, Iterator, Protocol
import zipfile

import github
import marko
import requests

import _exporters
import _parser.markdown

import _change_log_parser
import _integration_test_runner
import _change_log
import _github


_STRUCTURIZR_CLI_ARCHIVE_NAME: Final = "structurizr-cli.zip"
_STRUCTURIZR_CLI_DIR: Final = "structurizr-cli"


@dataclass
class _TestCaseInfo:
    name: str
    workspace_path: Path
    run_config: _integration_test_runner.TestCaseRunConfiguration


@dataclass
class _StructurizrCliRelease:
    version: str
    url: str

    def __str__(self) -> str:
        return f"StructurizrCli(version={self.version})"


@dataclass
class _StructurizrLiteRelease:
    version: str
    url: str

    def __str__(self) -> str:
        return f"StructurizrLite(version={self.version})"


type _ExporterRelease = _StructurizrCliRelease | _StructurizrLiteRelease


class _ExporterFactory(Protocol):
    def __call__(self, java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrWorkspaceExporter:
        ...


@dataclass
class ValidateStructureArgs:
    file: Path


@dataclass
class ValidateIssuesArgs:
    file: Path
    pr_location: _github.PullRequestLocation
    github_token: str | None


@dataclass
class ValidateIssueAddedArgs:
    file: Path
    pr_location: _github.PullRequestLocation
    github_token: str | None


@dataclass
class TestSyntaxPluginArgs:
    syntax_plugin_path: Path
    java_path: Path
    env_config: Path
    test_case_config_file: Path


class ValidationIssueError(Exception):
    def __init__(self, problem_issues: list[_github.IssueInfo]) -> None:
        self.problem_issues = problem_issues
        super().__init__(
            f"Validation failed for issues: [\n\t{',\n\t'.join(str(issue) for issue in problem_issues)}\n]"
        )


class IssueNotFoundError(Exception):
    def __init__(self, issue_id: int) -> None:
        super().__init__(
            f"Issue with ID {issue_id} not found in the last version changes"
        )
        self.issue_id = issue_id


def _parse_change_log(file: Path, log: logging.Logger) -> _change_log.ChangeLog:
    md = marko.Markdown()
    content = file.read_text(encoding="utf-8")
    elements = md.parse(content).children
    cursor = _parser.markdown.MarkdownCursor(elements)

    change_log, _ = _change_log_parser.CHANGE_LOG_PARSER.parse(
        (_change_log.create_empty_log(), cursor)
    )

    log.debug(f"Parsed CHANGELOG: {change_log}")
    return change_log


@contextlib.contextmanager
def _log_action(log: logging.Logger, action: str) -> Iterator[None]:
    log.debug(f"{action}: started")

    try:
        yield
    except Exception as e:
        log.debug(f"{action}: failed: {e}")
        raise
    else:
        log.debug(f"{action}: completed")


def _extract_issue_links(change_log: _change_log.ChangeLog) -> Iterator[str]:
    for version_changes in change_log.version_changes:
        all_version_changes = itertools.chain(
            version_changes.external_changes,
            version_changes.internal_changes,
        )

        for change in all_version_changes:
            yield change.link


def _init_github_client(token: str | None) -> github.Github:
    return github.Github(token)


def validate_structure(args: ValidateStructureArgs, log: logging.Logger) -> None:
    if not args.file.exists():
        raise FileNotFoundError(f"File {args.file} does not exist")

    with _log_action(log, "Validating CHANGELOG structure"):
        _parse_change_log(args.file, log)

    log.info("Validation passed successfully!")


def validate_issues(args: ValidateIssuesArgs, log: logging.Logger) -> None:
    if not args.file.exists():
        raise FileNotFoundError(f"File {args.file} does not exist")

    with _log_action(log, "Validating Issues states"):
        with _log_action(log, "Parse CHANGELOG file"):
            change_log = _parse_change_log(args.file, log)

        with _log_action(log, "Get issue infos"):
            github_client = _init_github_client(args.github_token)
            issue_links = _extract_issue_links(change_log)
            issue_infos = [
                _github.get_issue_info(github_client, issue_link)
                for issue_link in issue_links
            ]

        with _log_action(log, "Get linkes issue infos"):
            pr_info = _github.get_pull_request_info(
                github_token=args.github_token,
                pr_location=args.pr_location,
            )
            linked_issue_ids = {issue.number for issue in pr_info.pinned_issues}

        with _log_action(log, "Check issues state"):
            problem_issues: list[_github.IssueInfo] = []

            for issue_info in issue_infos:
                log.debug(
                    f"Issue (number={issue_info.number}) state: is_closed={issue_info.is_closed}"
                )

                expected_to_be_closed = issue_info.number not in linked_issue_ids
                log.debug(f"Expected to be closed: {expected_to_be_closed}")

                if issue_info.is_closed != expected_to_be_closed:
                    problem_issues.append(issue_info)

            if problem_issues:
                raise ValidationIssueError(problem_issues)

    log.info("All issues states are valid.")


def _get_last_version_change_issues(
    change_log: _change_log.ChangeLog,
    github_token: str | None,
    log: logging.Logger,
) -> list[_github.IssueInfo]:
    if not change_log.version_changes:
        return []

    last_version_changes = change_log.version_changes[0]
    log.debug(f"Last version changes: {last_version_changes}")

    all_version_changes = itertools.chain(
        last_version_changes.external_changes,
        last_version_changes.internal_changes,
    )

    issues: list[_github.IssueInfo] = []
    for change in all_version_changes:
        issues.append(
            _github.get_issue_info(
                _init_github_client(github_token),
                change.link,
            )
        )

    return issues


def validate_issue_added(args: ValidateIssueAddedArgs, log: logging.Logger) -> None:
    if not args.file.exists():
        raise FileNotFoundError(f"File {args.file} does not exist")

    with _log_action(log, "Validating Issue added"):
        with _log_action(log, "Parse CHANGELOG file"):
            change_log = _parse_change_log(args.file, log)

        with _log_action(log, "Get linked issue infos"):
            pr_info = _github.get_pull_request_info(
                github_token=args.github_token,
                pr_location=args.pr_location,
            )
            linked_issue_ids = {issue.number for issue in pr_info.pinned_issues}

        with _log_action(log, "Get issues in last version changes"):
            issue_infos = _get_last_version_change_issues(
                change_log, args.github_token, log
            )

            log.debug("Issue infos:")
            for issue_info in issue_infos:
                log.debug(f"\t- {issue_info}")

        with _log_action(log, "Check issue states"):
            problem_issues: list[_github.IssueInfo] = []

            for linked_issue_id in linked_issue_ids:
                for issue_info in issue_infos:
                    if issue_info.number != linked_issue_id:
                        continue

                    if issue_info.is_closed:
                        problem_issues.append(issue_info)
                        break
                    else:
                        log.debug(f"Issue #{linked_issue_id} validation passed")
                        break

                else:
                    raise IssueNotFoundError(linked_issue_id)

            if problem_issues:
                raise ValidationIssueError(problem_issues)

    log.info(f"Linked issue states are valid")


def _install_file(
    url: str, output_path: Path, log: logging.Logger, *, percent_threshold: float = 10.0
) -> None:
    with requests.get(url, stream=True) as response:
        with output_path.open("wb") as file:
            total_installed_bytes = 0
            last_logged_percent = 0.0
            content_length = response.headers.get("Content-Length", None)
            file_size = int(content_length) if content_length is not None else None

            for chunk in response.iter_content(chunk_size=8_192):
                if not isinstance(chunk, bytes) or not chunk:
                    continue

                file.write(chunk)
                total_installed_bytes += len(chunk)

                if file_size is None:
                    continue

                percent = total_installed_bytes / file_size * 100.0

                if percent - last_logged_percent < percent_threshold:
                    continue

                log.debug(f"Installed {percent:.2f}%")
                last_logged_percent = percent


def _extract_test_cases_info_from_file(config_file: Path) -> list[_TestCaseInfo]:
    raw_infos = json.loads(config_file.read_text())
    test_cases_info: list[_TestCaseInfo] = []

    for raw_info in raw_infos:
        match raw_info:
            case {
                "result": "success",
                "name": str(name),
                "workspace": str(workspace_path),
                "export_result_file": str(result_file_path),
            }:
                test_cases_info.append(
                    _TestCaseInfo(
                        name=name,
                        workspace_path=Path(workspace_path),
                        run_config=_integration_test_runner.SuccessTestCase(
                            name=name,
                            expected_export_result_file=Path(result_file_path),
                        ),
                    )
                )

            case {
                "result": "fail",
                "name": str(name),
                "workspace": str(workspace_path),
                "exit_code": int(exit_code),
                "error_message": str(error_message),
            }:
                test_cases_info.append(
                    _TestCaseInfo(
                        name=name,
                        workspace_path=Path(workspace_path),
                        run_config=_integration_test_runner.FailTestCase(
                            name=name,
                            exit_code=exit_code,
                            error_message=error_message,
                        ),
                    )
                )

            case _:
                raise ValueError(
                    "Unknown tets case configuration:\n{}".format(
                        json.dumps(raw_info, indent=4)
                    )
                )

    return test_cases_info


def _get_exporter_release(raw_release: Any) -> _ExporterRelease | None:
    match raw_release:
        case {"type": "structurizr-cli", "version": str(version), "url": str(url)}:
            return _StructurizrCliRelease(
                version=version,
                url=url,
            )
        case {"type": "structurizr-lite", "version": str(version), "url": str(url)}:
            return _StructurizrLiteRelease(
                version=version,
                url=url,
            )
        case _:
            return None


def _extract_exporter_releases_from_file(config_file: Path) -> list[_ExporterRelease]:
    raw_data = json.loads(config_file.read_text())
    releases: list[_ExporterRelease] = []

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


def _get_structurizr_cli_exporter_factory(release: _StructurizrCliRelease, temp_dir_path: Path, log: logging.Logger) -> _ExporterFactory:
    structurizr_archive_path = temp_dir_path / _STRUCTURIZR_CLI_ARCHIVE_NAME
    structurizr_cli_dir = temp_dir_path / _STRUCTURIZR_CLI_DIR

    with _log_action(log, "Install structurizr cli"):
        _install_file(
            url=release.url,
            output_path=structurizr_archive_path,
            log=log,
        )

    with _log_action(log, "Extract structurizr cli"):
        with zipfile.ZipFile(structurizr_archive_path, "r") as archive:
            archive.extractall(structurizr_cli_dir)

    def _create_structurizr_cli_exporter(java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrCli:
        return _exporters.StructurizrCli(
            structurizr_cli_dir=structurizr_cli_dir,
            java_path=java_path,
            syntax_plugin_path=syntax_plugin_path,
        )

    return _create_structurizr_cli_exporter


def _get_structurizr_lite_exporter_factory(release: _StructurizrLiteRelease, temp_dir_path: Path, log: logging.Logger) -> _ExporterFactory:
    structurizr_lite_dir = temp_dir_path / "structurizr-lite"
    structurizr_lite_dir.mkdir()

    structurizr_lite_war_file = structurizr_lite_dir / "structurizr-lite.war"

    with _log_action(log, "Install structurizr lite"):
        _install_file(
            url=release.url,
            output_path=structurizr_lite_war_file,
            log=log,
        )

    def _create_structurizr_lite_exporter(java_path: Path, syntax_plugin_path: Path) -> _exporters.StructurizrLite:
        return _exporters.StructurizrLite(
            structurizr_lite_dir=structurizr_lite_dir,
            java_path=java_path,
            syntax_plugin_path=syntax_plugin_path,
            stdout_path=temp_dir_path / "stdout.txt",
            stderr_path=temp_dir_path / "stderr.txt",
        )

    return _create_structurizr_lite_exporter


def _get_exporter_factory(release: _ExporterRelease, temp_dir_path: Path, log: logging.Logger) -> _ExporterFactory:
    match release:
        case _StructurizrCliRelease() as cli_release:
            return _get_structurizr_cli_exporter_factory(cli_release, temp_dir_path, log)
        case _StructurizrLiteRelease() as lite_release:
            return _get_structurizr_lite_exporter_factory(lite_release, temp_dir_path, log)


def test_syntax_plugin(args: TestSyntaxPluginArgs, log: logging.Logger) -> None:
    exporter_releases = _extract_exporter_releases_from_file(args.env_config)

    with _log_action(log, "Extract test case configuration"):
        test_cases_info = _extract_test_cases_info_from_file(
            args.test_case_config_file
        )

    for exporter_release in exporter_releases:
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_dir_path = Path(temp_dir)

            with _log_action(log, "Test pattern-syntax-plugin work in specified environment"):
                log.debug(
                    "Context:\n"
                    f"- Exporter: {exporter_release}\n"
                )

                exporter_factory = _get_exporter_factory(exporter_release, temp_dir_path, log)

                with _log_action(log, "Run integration tests"):
                    for test_case_info in test_cases_info:
                        log.info(f"Run '{test_case_info.name}' test case ...")

                        exporter = exporter_factory(
                            java_path=args.java_path,
                            syntax_plugin_path=args.syntax_plugin_path,
                        )

                        try:
                            _integration_test_runner.run_integration_test_case(
                                run_config=test_case_info.run_config,
                                exporter=exporter,
                                workspace_path=test_case_info.workspace_path,
                            )
                        finally:
                            exporter.close()

                        log.info(f"Run '{test_case_info.name}' test case ... ok")

        log.info("All checks passed!")


__all__ = [
    "validate_structure",
    "validate_issues",
    "validate_issue_added",
    "test_syntax_plugin",
    "ValidateStructureArgs",
    "ValidateIssuesArgs",
    "ValidateIssueAddedArgs",
    "TestSyntaxPluginArgs",
    "ValidationIssueError",
    "IssueNotFoundError",
]
