from dataclasses import dataclass
from typing import Callable, Sequence
import marko.element
import marko.inline


@dataclass
class Header[_T]:
    level: int
    content: _T


@dataclass
class ItemList[_T]:
    items: _T


Elements = Sequence[marko.element.Element]


def validate_element_type[_T](expected_type: type[_T], elements: Elements) -> tuple[_T, Elements]:
    assert len(elements) > 0
    element = elements[0]
    assert isinstance(element, expected_type)

    return element, elements[1:]


def parse_header[_T = Elements](
    elements: Elements,
    parse_content: Callable[[Elements], _T] = lambda x: x,
) -> tuple[Header[_T], Elements]:
    header_element, elements = validate_element_type(marko.block.Heading, elements)
    header = Header(
        level=header_element.level,
        content=parse_content(header_element.children),
    )

    return header, elements


def parse_item_list[_T = Elements](
    elements: Elements,
    parse_item: Callable[[Elements], _T] = lambda x: x,
) -> tuple[ItemList[_T], Elements]:
    if len(elements) == 0:
        return ItemList(items=[]), elements

    list_element, elements = validate_element_type(marko.block.List, elements)
    items = [parse_item(item.children) for item in list_element.children]
    return ItemList(items=items), elements


def skip_blank_lines(elements: Elements) -> Elements:
    while True:
        try:
            _, elements = validate_element_type(marko.block.BlankLine, elements)
        except AssertionError:
            break

    return elements


def parse_raw_text(elements: Elements) -> str:
    raw_text, elements = validate_element_type(marko.inline.RawText, elements)
    assert len(elements) == 0
    return raw_text.children
