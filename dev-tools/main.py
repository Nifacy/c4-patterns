from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from marko import Markdown
import re

import _parser.base
import _parser.markdown

import marko.element

_change_item_parser: _parser.base.IParser[None, marko.element.Element] = (
    _parser.base.Chain(
        _parser.markdown.Paragraph(
            _parser.base.Chain(
                _parser.markdown.RawText(re.compile(r"^.+ \($")),
                _parser.markdown.Link(re.compile(r"^#\d+$")),
                _parser.markdown.RawText(re.compile(r"\)")),
            ),
        ),
        _parser.markdown.EOF(),
    )
)


_changelog_parser: _parser.base.IParser[None, marko.element.Element] = (
    _parser.base.Chain(
        _parser.markdown.Header(1, re.compile("Changes")),
        _parser.base.Repeat(
            _parser.base.Chain(
                _parser.markdown.BlankLines(),
                _parser.markdown.Header(2, re.compile(r"\[\d+\.\d+\]")),
                _parser.markdown.BlankLines(),
                _parser.markdown.Header(3, re.compile("External")),
                _parser.markdown.BlankLines(),
                _parser.markdown.List(_change_item_parser),
                _parser.base.Optional(
                    _parser.base.Chain(
                        _parser.markdown.BlankLines(),
                        _parser.markdown.Header(3, re.compile("Internal")),
                    ),
                    _parser.base.Chain(
                        _parser.markdown.BlankLines(),
                        _parser.markdown.List(_change_item_parser),
                    ),
                ),
            ),
            next_parser=_parser.base.Chain(
                _parser.markdown.BlankLines(),
                _parser.markdown.EOF(),
            ),
        ),
    )
)


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

    md = Markdown()
    content = conf.file.read_text(encoding="utf-8")
    elements = md.parse(content).children
    cursor = _parser.markdown.MarkdownCursor(elements)

    _changelog_parser.parse((None, cursor))
    print("Validation passed successfully!")


if __name__ == "__main__":
    configuration = parse_args()

    try:
        main(configuration)
        exit(0)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        exit(1)
