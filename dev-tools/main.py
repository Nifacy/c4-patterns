from ast import Call
from dataclasses import dataclass
from pathlib import Path
import re
from tokenize import group
from typing import Callable, Sequence, TypeVarTuple
import marko
import marko.element
import marko.inline


@dataclass
class Header[_T]:
    level: int
    content: _T


type ItemList[_T] = list[_T]


Elements = Sequence[marko.element.Element]


def _validate_header[_T](
    elements: Elements,
    validate_content: Callable[[Elements], _T] = lambda x: x,
) -> tuple[Header[_T], Elements]:
    print(elements)    

    assert len(elements) > 0
    header_element = elements[0]
    assert isinstance(header_element, marko.block.Heading)

    header = Header(header_element.level, validate_content(header_element.children))
    return header, elements[1:]



def _validate_item_list[_T](
    elements: Elements,
    validate_item: Callable[[Elements], _T] = lambda x: x,
) -> tuple[ItemList[_T], Elements]:
    if len(elements) == 0:
        return [], elements

    list_element = elements[0]
    assert isinstance(list_element, marko.block.List)

    result = [validate_item(item.children) for item in list_element.children]
    return result, elements[1:]


@dataclass
class IssueInfo:
    number: int
    link: str


@dataclass
class ChangeItem:
    description: str
    issue_info: IssueInfo


def _validate_issue_info(link: marko.inline.Link) -> IssueInfo:
    assert len(link.children) == 1
    raw_text = link.children[0]
    assert isinstance(raw_text, marko.inline.RawText)

    assert re.match(r'#\d+', raw_text.children)

    return IssueInfo(
        number=int(raw_text.children.lstrip('#')),
        link=link.dest,
    )


def _validate_change_item(elements: Elements) -> ChangeItem:
    assert len(elements) == 1
    paragraph = elements[0]
    assert isinstance(paragraph, marko.block.Paragraph)

    assert len(paragraph.children) == 3
    prefix, link, suffix = paragraph.children

    assert isinstance(prefix, marko.inline.RawText)
    assert re.match(r'.* \(', prefix.children)

    assert isinstance(suffix, marko.inline.RawText)
    assert re.match(r'\)', suffix.children)

    assert isinstance(link, marko.inline.Link)
    
    return ChangeItem(
        description=prefix.children.rstrip('( '),
        issue_info=_validate_issue_info(link),
    )


def _skip_blank_lines(elements: Elements) -> tuple[None, Elements]:
    while True:
        if len(elements) == 0:
            break

        blank_line = elements[0]
        if not isinstance(blank_line, marko.block.BlankLine):
            break

        elements = elements[1:]

    return None, elements


@dataclass
class VersionChanges:
    version: str
    external: list[ChangeItem]
    internal: list[ChangeItem]


def _validate_raw_text(elements: Elements) -> str:
    assert len(elements) == 1
    assert isinstance(elements[0], marko.inline.RawText)
    return elements[0].children


def _validate_changes_group(group_name: str, elements: Elements) -> tuple[list[ChangeItem] | None, Elements]:
    try:
        header, next_elements = _validate_header(elements, validate_content=_validate_raw_text)
        assert header.content == group_name
    except AssertionError:
        return None, elements

    assert header.level == 3
    _, next_elements = _skip_blank_lines(next_elements)
    return _validate_item_list(
        elements=next_elements,
        validate_item=_validate_change_item,
    )


def _validate_version_changes(elements: Elements) -> tuple[VersionChanges, Elements]:
    print('Validate Version Changes: ', elements)

    version_header, elements = _validate_header(elements, _validate_raw_text)
    assert version_header.level == 2
    assert re.match(r'\[.+\]', version_header.content)

    _, elements = _skip_blank_lines(elements)

    external_changes, elements = _validate_changes_group(
        group_name='External',
        elements=elements,
    )

    _, elements = _skip_blank_lines(elements)

    internal_changes, elements = _validate_changes_group(
        group_name='Internal',
        elements=elements,
    )

    _, elements = _skip_blank_lines(elements)

    version_changes = VersionChanges(
        version=version_header.content.strip('[]'),
        external=external_changes or [],
        internal=internal_changes or [],
    )

    return version_changes, elements


@dataclass
class ChangeLog:
    version_changes: list[VersionChanges]


def _validate_change_log(elements: Elements) -> ChangeLog:
    header, elements = _validate_header(elements, _validate_raw_text)
    assert header.level == 1
    assert header.content == 'Changes'

    _, elements = _skip_blank_lines(elements)

    version_changes_list = []
    while len(elements) > 0:
        version_changes, elements = _validate_version_changes(elements)
        print(f'Version Changes: {version_changes}')

        version_changes_list.append(version_changes)
        _, elements = _skip_blank_lines(elements)

    return ChangeLog(
        version_changes=version_changes_list,
    )




ast = marko.Markdown().parse(Path('file.md').read_text())


print(_validate_change_log(ast.children))
