import argparse
import logging
from pathlib import Path
import sys

import _usecases

type _ParsedArgs = _usecases.ValidateStructureArgs | _usecases.ValidateIssuesArgs | _usecases.ValidateIssueAddedArgs


def _init_validate_structure_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "file",
        type=Path,
        help="Path to the CHANGELOG file",
    )


def _init_validate_issues_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("file", type=Path, help="Path to the CHANGELOG file")
    parser.add_argument(
        "--open-ids",
        nargs="*",
        default=None,
        type=int,
        help="List of issue IDs expected to be open. If not specified, all issues must be closed",
    )


def _init_validate_issue_added_parser(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("file", type=Path, help="Path to the CHANGELOG file")
    parser.add_argument("id", help="ID of the issue to check")


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


def _init_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Dev Tools CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    changelog_parser = subparsers.add_parser(
        "changelog", help="Changelog validation commands"
    )
    _init_changelog_parser(changelog_parser)

    return parser


def _extract_parsed_arguments(args: argparse.Namespace) -> _ParsedArgs:
    match args.command:
        case "changelog":
            match args.changelog_command:
                case "validate-structure":
                    return _usecases.ValidateStructureArgs(file=args.file)
                case "validate-issues":
                    return _usecases.ValidateIssuesArgs(
                        file=args.file, open_ids=args.open_ids
                    )
                case "validate-issue-added":
                    return _usecases.ValidateIssueAddedArgs(
                        file=args.file, issue_id=args.id
                    )
                case _:
                    raise ValueError(
                        f"Unknown changelog command: {args.changelog_command}"
                    )
        case _:
            raise ValueError(f"Unknown command: {args.command}")


def _parse_args() -> _ParsedArgs:
    parser = _init_parser()
    args = parser.parse_args()
    return _extract_parsed_arguments(args)


def main() -> None:
    args = _parse_args()
    log = logging.getLogger("devtools-cli")

    match args:
        case _usecases.ValidateStructureArgs():
            _usecases.validate_structure(args, log)
        case _usecases.ValidateIssuesArgs():
            _usecases.validate_issues(args, log)
        case _usecases.ValidateIssueAddedArgs():
            _usecases.validate_issue_added(args, log)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    try:
        main()
    except Exception as e:
        logging.error(f"Error: {e}")
        sys.exit(1)
    else:
        sys.exit(0)
