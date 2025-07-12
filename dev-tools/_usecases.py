import contextlib
from dataclasses import dataclass
import itertools
import logging
from pathlib import Path
from typing import Iterator

import github
import marko

import _parser.markdown

import _change_log_parser
import _change_log
import _issue


@dataclass
class ValidateStructureArgs:
    file: Path


@dataclass
class ValidateIssuesArgs:
    file: Path
    open_ids: list[int] | None


@dataclass
class ValidateIssueAddedArgs:
    file: Path
    issue_id: int


class ValidationIssueError(Exception):
    def __init__(self, problem_issues: list[_issue.IssueInfo]) -> None:
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


def _parse_change_log(file: Path) -> _change_log.ChangeLog:
    md = marko.Markdown()
    content = file.read_text(encoding="utf-8")
    elements = md.parse(content).children
    cursor = _parser.markdown.MarkdownCursor(elements)

    change_log, _ = _change_log_parser.CHANGE_LOG_PARSER.parse(
        (_change_log.create_empty_log(), cursor)
    )
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


def validate_structure(args: ValidateStructureArgs, log: logging.Logger) -> None:
    if not args.file.exists():
        raise FileNotFoundError(f"File {args.file} does not exist")

    with _log_action(log, "Validating CHANGELOG structure"):
        _parse_change_log(args.file)

    log.info("Validation passed successfully!")


def validate_issues(args: ValidateIssuesArgs, log: logging.Logger) -> None:
    if not args.file.exists():
        raise FileNotFoundError(f"File {args.file} does not exist")

    def _expected_to_be_closed(issue_info: _issue.IssueInfo) -> bool:
        return args.open_ids is None or issue_info.number in args.open_ids

    with _log_action(log, "Validating Issues states"):
        with _log_action(log, "Parse CHANGELOG file"):
            change_log = _parse_change_log(args.file)

        with _log_action(log, "Extract issue infos"):
            github_client = github.Github()
            issue_links = _extract_issue_links(change_log)
            issue_infos = [
                _issue.extract_issue_info(github_client, issue_link)
                for issue_link in issue_links
            ]

        with _log_action(log, "Check issues state"):
            problem_issues: list[_issue.IssueInfo] = []

            for issue_info in issue_infos:
                log.debug(
                    f"Issue (number={issue_info.number}) state: is_closed={issue_info.is_closed}"
                )

                expected_to_be_closed = _expected_to_be_closed(issue_info)
                log.debug(f"Expected to be closed: {expected_to_be_closed}")

                if issue_info.is_closed != expected_to_be_closed:
                    problem_issues.append(issue_info)

            if problem_issues:
                raise ValidationIssueError(problem_issues)

    log.info("All issues states are valid.")


def _find_issue_in_last_version_changes(
    change_log: _change_log.ChangeLog, issue_id: int
) -> _issue.IssueInfo:
    if not change_log.version_changes:
        raise IssueNotFoundError(issue_id)

    last_version_changes = change_log.version_changes[0]
    all_version_changes = itertools.chain(
        last_version_changes.external_changes,
        last_version_changes.internal_changes,
    )

    for change in all_version_changes:
        issue_info = _issue.extract_issue_info(github.Github(), change.link)
        if issue_info.number == issue_id:
            return issue_info

    raise IssueNotFoundError(issue_id)


def validate_issue_added(args: ValidateIssueAddedArgs, log: logging.Logger) -> None:
    if not args.file.exists():
        raise FileNotFoundError(f"File {args.file} does not exist")

    with _log_action(log, "Validating Issue added"):
        with _log_action(log, "Parse CHANGELOG file"):
            change_log = _parse_change_log(args.file)

        with _log_action(log, "Find issue in last version changes"):
            issue_info = _find_issue_in_last_version_changes(change_log, args.issue_id)

        with _log_action(log, "Check issue state"):
            if issue_info.is_closed:
                raise ValidationIssueError([issue_info])

    log.info(f"Issue #{args.issue_id} state is valid")


__all__ = [
    "validate_structure",
    "validate_issues",
    "validate_issue_added",
    "ValidateStructureArgs",
    "ValidateIssuesArgs",
    "ValidateIssueAddedArgs",
    "ValidationIssueError",
    "IssueNotFoundError",
]
