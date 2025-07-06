from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import sys
from typing import NoReturn
from marko import Markdown
import re

import _validation


_change_item_validator = _validation.Chain(
    _validation.ValidateParagraph(
        _validation.Chain(
            _validation.ValidateRawText(re.compile(r"^.+ \($")),
            _validation.ValidateLink(re.compile(r"^#\d+$")),
            _validation.ValidateRawText(re.compile(r"\)")),
        ),
    ),
    _validation.ValidateEOF(),
)


_changelog_validator = _validation.Chain(
    _validation.ValidateHeader(1, re.compile("Changes")),
    _validation.Repeat(
        _validation.Chain(
            _validation.SkipBlankLines(),
            _validation.ValidateHeader(2, re.compile(r"\[\d+\.\d+\]")),
            _validation.SkipBlankLines(),
            _validation.ValidateHeader(3, re.compile("External")),
            _validation.SkipBlankLines(),
            _validation.ValidateList(_change_item_validator),
            _validation.Optional(
                _validation.Chain(
                    _validation.SkipBlankLines(),
                    _validation.ValidateHeader(3, re.compile("Internal")),
                ),
                _validation.Chain(
                    _validation.SkipBlankLines(),
                    _validation.ValidateList(_change_item_validator),
                ),
            ),
        ),
        next_validator=_validation.Chain(
            _validation.SkipBlankLines(),
            _validation.ValidateEOF(),
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
    cursor = _validation.Cursor(elements)

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
