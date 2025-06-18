import re
import marko
import marko.inline
from _types import ChangeItem, ChangeLog, IssueInfo, VersionChanges
from _markdown import Elements, parse_header, parse_item_list, parse_raw_text, skip_blank_lines, validate_element_type



def _parse_issue_info(link: marko.inline.Link) -> IssueInfo:
    title = parse_raw_text(link.children)
    assert re.match(r"#\d+", title)

    return IssueInfo(
        number=int(title.lstrip("#")),
        link=link.dest,
    )


def _parse_change_item(elements: Elements) -> ChangeItem:
    paragraph, elements = validate_element_type(marko.block.Paragraph, elements)
    assert len(elements) == 0

    paragraph_elements = paragraph.children
    prefix, paragraph_elements = validate_element_type(marko.inline.RawText, paragraph_elements)
    link, paragraph_elements = validate_element_type(marko.inline.Link, paragraph_elements)
    suffix, paragraph_elements = validate_element_type(marko.inline.RawText, paragraph_elements)
    assert len(paragraph_elements) == 0

    assert re.match(r".* \(", prefix.children)
    assert re.match(r"\)", suffix.children)

    return ChangeItem(
        description=prefix.children.rstrip("( "),
        issue_info=_parse_issue_info(link),
    )


def _parse_changes_group(
    group_name: str,
    elements: Elements,
) -> tuple[list[ChangeItem] | None, Elements]:
    try:
        header, next_elements = parse_header(
            elements, parse_raw_text
        )
        assert header.content == group_name
    except AssertionError:
        return None, elements

    assert header.level == 3
    next_elements = skip_blank_lines(next_elements)
    return parse_item_list(
        elements=next_elements,
        parse_item=_parse_change_item,
    )


def _parse_version_changes(elements: Elements) -> tuple[VersionChanges, Elements]:
    version_header, elements = parse_header(elements, parse_raw_text)
    assert version_header.level == 2
    assert re.match(r"\[.+\]", version_header.content)

    elements = skip_blank_lines(elements)
    external_changes, elements = _parse_changes_group(
        group_name="External",
        elements=elements,
    )

    elements = skip_blank_lines(elements)
    internal_changes, elements = _parse_changes_group(
        group_name="Internal",
        elements=elements,
    )

    elements = skip_blank_lines(elements)
    version_changes = VersionChanges(
        version=version_header.content.strip("[]"),
        external=external_changes or [],
        internal=internal_changes or [],
    )

    return version_changes, elements


def parse_change_log(elements: Elements) -> ChangeLog:
    header, elements = parse_header(elements, parse_raw_text)
    assert header.level == 1
    assert header.content == "Changes"

    elements = skip_blank_lines(elements)

    version_changes_list = []
    while len(elements) > 0:
        version_changes, elements = _parse_version_changes(elements)
        version_changes_list.append(version_changes)
        elements = skip_blank_lines(elements)

    return ChangeLog(
        version_changes=version_changes_list,
    )
