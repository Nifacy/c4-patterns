from dataclasses import dataclass
import itertools
import logging
from pathlib import Path
import sys
from typing import Final, Iterator

import github
import marko
import pytest

import _parser.markdown

import _change_log_parser
import _change_log
import _github
import _logging_tools


_CUR_DIR_PATH: Final = Path(__file__).parent
_SYNTAX_PLUGIN_TEST_FILE_PATH: Final = _CUR_DIR_PATH / "tests" / "test_syntax_plugin.py"


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
    samples_dir: Path


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

    with _logging_tools.log_action(log, "Validating CHANGELOG structure"):
        _parse_change_log(args.file, log)

    log.info("Validation passed successfully!")


def validate_issues(args: ValidateIssuesArgs, log: logging.Logger) -> None:
    if not args.file.exists():
        raise FileNotFoundError(f"File {args.file} does not exist")

    with _logging_tools.log_action(log, "Validating Issues states"):
        with _logging_tools.log_action(log, "Parse CHANGELOG file"):
            change_log = _parse_change_log(args.file, log)

        with _logging_tools.log_action(log, "Get issue infos"):
            github_client = _init_github_client(args.github_token)
            issue_links = _extract_issue_links(change_log)
            issue_infos = [
                _github.get_issue_info(github_client, issue_link)
                for issue_link in issue_links
            ]

        with _logging_tools.log_action(log, "Get linkes issue infos"):
            pr_info = _github.get_pull_request_info(
                github_token=args.github_token,
                pr_location=args.pr_location,
            )
            linked_issue_ids = {issue.number for issue in pr_info.pinned_issues}

        with _logging_tools.log_action(log, "Check issues state"):
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

    with _logging_tools.log_action(log, "Validating Issue added"):
        with _logging_tools.log_action(log, "Parse CHANGELOG file"):
            change_log = _parse_change_log(args.file, log)

        with _logging_tools.log_action(log, "Get linked issue infos"):
            pr_info = _github.get_pull_request_info(
                github_token=args.github_token,
                pr_location=args.pr_location,
            )
            linked_issue_ids = {issue.number for issue in pr_info.pinned_issues}

        with _logging_tools.log_action(log, "Get issues in last version changes"):
            issue_infos = _get_last_version_change_issues(
                change_log, args.github_token, log
            )

            log.debug("Issue infos:")
            for issue_info in issue_infos:
                log.debug(f"\t- {issue_info}")

        with _logging_tools.log_action(log, "Check issue states"):
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


def test_syntax_plugin(args: TestSyntaxPluginArgs, log: logging.Logger) -> None:
    sys.exit(pytest.main([
        str(_SYNTAX_PLUGIN_TEST_FILE_PATH),
        f'--test-case-config={args.test_case_config_file.absolute()}',
        f'--env-config={args.env_config.absolute()}',
        f'--plugin-path={args.syntax_plugin_path.absolute()}',
        f'--java-path={args.java_path.absolute()}',
        f'--samples-dir={args.samples_dir.absolute()}',
        '--verbose',
        '--log-cli-level=DEBUG',
    ]))


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
