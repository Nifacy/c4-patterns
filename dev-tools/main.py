from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import NoReturn
from marko import Markdown
import re

from _validation import markdown as _md_validation
from _validation import base as _base_validation


_change_item_validator = _base_validation.Chain(
    _md_validation.ValidateParagraph(
        _base_validation.Chain(
            _md_validation.ValidateRawText(re.compile(r"^.+ \($")),
            _md_validation.ValidateLink(re.compile(r"^#\d+$")),
            _md_validation.ValidateRawText(re.compile(r"\)")),
        ),
    ),
    _md_validation.ValidateEOF(),
)


_changelog_validator = _base_validation.Chain(
    _md_validation.ValidateHeader(1, re.compile("Changes")),
    _base_validation.Repeat(
        _base_validation.Chain(
            _md_validation.SkipBlankLines(),
            _md_validation.ValidateHeader(2, re.compile(r"\[\d+\.\d+\]")),
            _md_validation.SkipBlankLines(),
            _md_validation.ValidateHeader(3, re.compile("External")),
            _md_validation.SkipBlankLines(),
            _md_validation.ValidateList(_change_item_validator),
            _base_validation.Optional(
                _base_validation.Chain(
                    _md_validation.SkipBlankLines(),
                    _md_validation.ValidateHeader(3, re.compile("Internal")),
                ),
                _base_validation.Chain(
                    _md_validation.SkipBlankLines(),
                    _md_validation.ValidateList(_change_item_validator),
                ),
            ),
        ),
        next_validator=_base_validation.Chain(
            _md_validation.SkipBlankLines(),
            _md_validation.ValidateEOF(),
        ),
    ),
)


@dataclass
class Configuration:
    file: Path


def parse_args() -> Configuration:
    parser = argparse.ArgumentParser(description="Validate CHANGELOG file structure")
    parser.add_argument("file", type=Path, help="Path to the CHANGELOG file")

    arguments = parser.parse_args()
    return Configuration(file=arguments.file)


def main(conf: Configuration) -> NoReturn:
    if not conf.file.exists():
        raise FileNotFoundError(f"File {conf.file} does not exist")

    md = Markdown()
    content = conf.file.read_text(encoding="utf-8")
    elements = md.parse(content).children
    cursor = _md_validation.MarkdownCursor(elements)

    _changelog_validator.validate(cursor)
    print("Validation passed successfully!")


if __name__ == "__main__":
    configuration = parse_args()

    try:
        main(configuration)
        exit(0)
    except Exception as e:
        print(f"error: {e}", file=sys.stderr)
        exit(1)
