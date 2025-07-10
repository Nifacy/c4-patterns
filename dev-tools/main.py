from __future__ import annotations

import argparse
from dataclasses import dataclass
import github
import itertools
from pathlib import Path
import sys
from typing import Callable, Iterator
from marko import Markdown
import re

import marko.inline

import _issue
import _parser.base
import _parser.markdown
import _change_log

import marko.element


type _ChangeLogParser = _parser.base.IParser[
    _change_log.ChangeLog,
    marko.element.Element,
]


def _change_item_parser(
    add_item: Callable[
        [_change_log.ChangeLog, _change_log.Change],
        _change_log.ChangeLog,
    ],
) -> _ChangeLogParser:
    def _add_item_to_change_log(
        log: _change_log.ChangeLog,
        paragraph: marko.block.Paragraph,
    ) -> _change_log.ChangeLog:
        raw_text, link, _ = paragraph.children

        assert isinstance(raw_text, marko.inline.RawText)
        change_description = raw_text.children.rstrip("(").strip()

        assert isinstance(link, marko.inline.Link)
        issue_link = link.dest

        return add_item(log, _change_log.Change(change_description, issue_link))

    # TODO: remove `parse_element` argument here in children parser
    # FIXME: fix error with parsing Paragraph before elements validation
    return _parser.base.Chain(
        _parser.markdown.Paragraph(
            _parser.base.Chain(
                _parser.markdown.RawText(re.compile(r"^.+ \($")),
                _parser.markdown.Link(re.compile(r"^#\d+$")),
                _parser.markdown.RawText(re.compile(r"\)")),
            ),
            parse_element=_add_item_to_change_log,
        ),
        _parser.markdown.EOF(),
    )


def _add_new_version(
    log: _change_log.ChangeLog, header: marko.block.Heading
) -> _change_log.ChangeLog:
    (raw_text,) = header.children

    assert isinstance(raw_text, marko.inline.RawText)
    version_id = raw_text.children.strip("[]")

    return _change_log.add_version(log, version_id)


_changelog_parser: _ChangeLogParser = _parser.base.Chain(
    _parser.markdown.Header(1, re.compile("Changes")),
    _parser.base.Repeat(
        _parser.base.Chain(
            _parser.markdown.BlankLines(),
            _parser.markdown.Header(2, re.compile(r"\[\d+\.\d+\]"), _add_new_version),
            _parser.markdown.BlankLines(),
            _parser.markdown.Header(3, re.compile("External")),
            _parser.markdown.BlankLines(),
            _parser.markdown.List(_change_item_parser(_change_log.add_external_change)),
            _parser.base.Optional(
                _parser.base.Chain(
                    _parser.markdown.BlankLines(),
                    _parser.markdown.Header(3, re.compile("Internal")),
                ),
                _parser.base.Chain(
                    _parser.markdown.BlankLines(),
                    _parser.markdown.List(
                        _change_item_parser(_change_log.add_internal_change)
                    ),
                ),
            ),
        ),
        next_parser=_parser.base.Chain(
            _parser.markdown.BlankLines(),
            _parser.markdown.EOF(),
        ),
    ),
)


def _extract_issue_links(change_log: _change_log.ChangeLog) -> Iterator[str]:
    for version_changes in change_log.version_changes:
        all_version_changes = itertools.chain(
            version_changes.external_changes,
            version_changes.internal_changes,
        )

        for change in all_version_changes:
            yield change.link


@dataclass
class Configuration:
    file: Path


def parse_args() -> Configuration:
    parser = argparse.ArgumentParser(description="Validate CHANGELOG file structure")
    parser.add_argument("file", type=Path, help="Path to the CHANGELOG file")

    arguments = parser.parse_args()
    return Configuration(file=arguments.file)


def main(conf: Configuration) -> None:
    if not conf.file.exists():
        raise FileNotFoundError(f"File {conf.file} does not exist")

    print("Validating CHANGELOG structure...")
    md = Markdown()
    content = conf.file.read_text(encoding="utf-8")
    elements = md.parse(content).children
    cursor = _parser.markdown.MarkdownCursor(elements)

    parse_result, _ = _changelog_parser.parse((_change_log.create_empty_log(), cursor))
    print("Validation passed successfully!")

    print("Check issues state ...")
    github_client = github.Github()
    issue_infos = [
        (
            issue_link,
            _issue.extract_issue_info(
                github_client=github_client,
                issue_link=issue_link,
            ),
        )
        for issue_link in _extract_issue_links(parse_result)
    ]

    for issue_link, issue_info in issue_infos:
        print(
            f'- Issue: {issue_link} is {"closed" if issue_info.is_closed else "open"}'
        )

    all_issues_closed = all(issue_info.is_closed for _, issue_info in issue_infos)
    if not all_issues_closed:
        raise ValueError("Not all issues are closed")
    else:
        print("All issues are closed, validation passed successfully!")


if __name__ == "__main__":
    configuration = parse_args()

    try:
        main(configuration)
        exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        exit(1)
