import argparse
from dataclasses import dataclass
from datetime import datetime
import logging
from pathlib import Path
import sys
import os
from typing import Final, Union

import _github
import _usecases

type _CommandArgs = Union[
    _usecases.ValidateStructureArgs,
    _usecases.ValidateIssuesArgs,
    _usecases.ValidateIssueAddedArgs,
    _usecases.TestSyntaxPluginArgs,
]


@dataclass
class _ParsedArgs:
    verbose: bool
    command_args: _CommandArgs


class _LoggerNameFormatter(logging.Formatter):
    _DEFAULT_DATE_FORMAT: Final = "%Y-%m-%d %H:%M:%S"

    def __init__(self, fmt: str | None = None, datefmt: str | None = None):
        super().__init__(fmt=fmt, datefmt=datefmt)

    def format(self, record: logging.LogRecord) -> str:
        ct = datetime.fromtimestamp(record.created).strftime(
            self.datefmt or self._DEFAULT_DATE_FORMAT
        )
        return f"{ct} [{record.levelname}] [{record.name}] {record.getMessage()}"


def _init_validate_structure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the CHANGELOG file",
    )


def _init_validate_issues_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--file", type=Path, required=True, help="Path to the CHANGELOG file"
    )
    parser.add_argument(
        "--repo",
        type=str,
        required=True,
        help="GitHub repository in the format 'owner/repo'",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        required=True,
        help="Pull request number to validate issues against",
    )


def _init_validate_issue_added_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--file", type=Path, required=True, help="Path to the CHANGELOG file"
    )
    parser.add_argument(
        "--repo",
        type=str,
        required=True,
        help="GitHub repository in the format 'owner/repo'",
    )
    parser.add_argument(
        "--pr-number",
        type=int,
        required=True,
        help="Pull request number to validate issues against",
    )


def _init_changelog_parser(parser: argparse.ArgumentParser) -> None:
    change_log_subparsers = parser.add_subparsers(
        dest="changelog_command", required=True
    )

    validate_structure_parser = change_log_subparsers.add_parser(
        "validate-structure",
        help="Validate the structure of the CHANGELOG file",
    )
    _init_validate_structure_parser(validate_structure_parser)

    validate_issues_parser = change_log_subparsers.add_parser(
        "validate-issues",
        help="Validate the states of issues in the CHANGELOG file",
    )
    _init_validate_issues_parser(validate_issues_parser)

    validate_issue_added_parser = change_log_subparsers.add_parser(
        "validate-issue-added",
        help="Validate that an issue is open and added in the newest changelog version",
    )
    _init_validate_issue_added_parser(validate_issue_added_parser)


def _init_integration_tests_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--plugin-path",
        type=Path,
        required=True,
        help="Path to pattern-syntax-plugin JAR archive",
    )

    parser.add_argument(
        "--java-path",
        type=Path,
        required=True,
        help="Path to java binary directory",
    )

    parser.add_argument(
        "--workspace-path",
        type=Path,
        required=True,
        help="Path to Structurizr workspace file",
    )

    parser.add_argument(
        "--expected_file",
        type=Path,
        required=True,
        help="Path to etalone exported JSON workspace file",
    )


def _init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dev Tools CLI")

    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        default=False,
        help="increase output verbosity",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)
    changelog_parser = subparsers.add_parser(
        "changelog", help="Changelog validation commands"
    )
    _init_changelog_parser(changelog_parser)

    integration_test_parser = subparsers.add_parser(
        "integration-tests",
        help="Run integration tests for patter-syntax-plugin",
    )
    _init_integration_tests_parser(integration_test_parser)

    return parser


def _extract_command_args(args: argparse.Namespace) -> _CommandArgs:
    match args.command:
        case "changelog":
            match args.changelog_command:
                case "validate-structure":
                    return _usecases.ValidateStructureArgs(file=args.file)
                case "validate-issues":
                    github_token = os.getenv("GITHUB_TOKEN")
                    return _usecases.ValidateIssuesArgs(
                        file=args.file,
                        pr_location=_github.PullRequestLocation(
                            repo=args.repo,
                            id=args.pr_number,
                        ),
                        github_token=github_token,
                    )
                case "validate-issue-added":
                    github_token = os.getenv("GITHUB_TOKEN")
                    return _usecases.ValidateIssueAddedArgs(
                        file=args.file,
                        pr_location=_github.PullRequestLocation(
                            repo=args.repo,
                            id=args.pr_number,
                        ),
                        github_token=github_token,
                    )
                case _:
                    raise ValueError(
                        f"Unknown changelog command: {args.changelog_command}"
                    )
        case "integration-tests":
            return _usecases.TestSyntaxPluginArgs(
                syntax_plugin_path=args.plugin_path,
                java_path=args.java_path,
                workspace_path=args.workspace_path,
                expected_file=args.expected_file,
            )
        case _:
            raise ValueError(f"Unknown command: {args.command}")


def _extract_parsed_arguments(args: argparse.Namespace) -> _ParsedArgs:
    command_args = _extract_command_args(args)

    return _ParsedArgs(
        verbose=args.verbose,
        command_args=command_args,
    )


def _parse_args() -> _ParsedArgs:
    parser = _init_parser()
    args = parser.parse_args()
    return _extract_parsed_arguments(args)


def _init_public_logger(logger: logging.Logger) -> None:
    info_handler = logging.StreamHandler(sys.stdout)
    info_handler.setLevel(logging.INFO)
    info_handler.addFilter(lambda record: record.levelno == logging.INFO)
    info_handler.setFormatter(logging.Formatter("%(message)s"))

    error_handler = logging.StreamHandler(sys.stderr)
    error_handler.setLevel(logging.ERROR)
    error_handler.addFilter(lambda record: record.levelno == logging.ERROR)
    error_handler.setFormatter(logging.Formatter("%(message)s"))

    logger.setLevel(logging.INFO)
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)


def _init_debug_logger(logger: logging.Logger) -> None:
    debug_handler = logging.StreamHandler(sys.stderr)
    debug_handler.setLevel(logging.DEBUG)
    debug_handler.setFormatter(_LoggerNameFormatter())

    logger.setLevel(logging.DEBUG)
    logger.addHandler(debug_handler)


def _init_logger(logger: logging.Logger, verbose: bool) -> None:
    if verbose:
        _init_debug_logger(logger)
    else:
        _init_public_logger(logger)


def main(log: logging.Logger, args: _ParsedArgs) -> None:
    match args.command_args:
        case _usecases.ValidateStructureArgs():
            _usecases.validate_structure(args.command_args, log)
        case _usecases.ValidateIssuesArgs():
            _usecases.validate_issues(args.command_args, log)
        case _usecases.ValidateIssueAddedArgs():
            _usecases.validate_issue_added(args.command_args, log)
        case _usecases.TestSyntaxPluginArgs():
            _usecases.test_syntax_plugin(args.command_args, log)


if __name__ == "__main__":
    args = _parse_args()
    log = logging.getLogger("devtools-cli")
    _init_logger(log, args.verbose)

    try:
        main(log, args)
    except Exception as e:
        log.error(f"Error: {e}")
        sys.exit(1)
    else:
        sys.exit(0)
