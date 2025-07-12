import _parser.base
import _parser.markdown
import _change_log

import marko.element
import marko.inline

from typing import Callable
import re


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


CHANGE_LOG_PARSER: _ChangeLogParser = _parser.base.Chain(
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

__all__ = [
    "CHANGE_LOG_PARSER",
]
