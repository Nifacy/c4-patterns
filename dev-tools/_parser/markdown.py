from __future__ import annotations

from typing import Callable, NoReturn, Sequence, override
import marko.element
import marko.block
import marko.inline
import re

from . import base


class MarkdownCursor(base.Cursor[marko.element.Element]):
    def __init__(self, elements: Sequence[marko.element.Element], index: int = 0):
        self.__elements = elements
        self.__index = index

    def next(self) -> tuple[marko.element.Element | None, MarkdownCursor]:
        if self.__index >= len(self.__elements):
            return None, self
        return self.__elements[self.__index], MarkdownCursor(
            self.__elements, self.__index + 1
        )


class _ElementParser[_V, _T: marko.element.Element](
    base.IParser[_V, marko.element.Element]
):
    def __init__(
        self,
        expected_type: type[_T],
        children_parser: base.IParser[_V, marko.element.Element] | None = None,
        parse_element: Callable[[_V, _T], _V] | None = None,
    ):
        self.__expected_type = expected_type
        self.__children_parser = children_parser
        self.__parse_element = parse_element

    def parse(
        self, state: base.State[_V, marko.element.Element]
    ) -> base.State[_V, marko.element.Element]:
        parsed_value, cursor = state
        current_element, next_cursor = cursor.next()

        if current_element is None:
            self.__raise_eof_error()

        if not isinstance(current_element, self.__expected_type):
            self.__raise_wrong_type_error(current_element)

        self._validate_element(current_element)

        if self.__parse_element is not None:
            parsed_value = self.__parse_element(parsed_value, current_element)

        if self.__children_parser is not None:
            parsed_value, _ = self.__children_parser.parse(
                (
                    parsed_value,
                    MarkdownCursor(current_element.children),  # type: ignore
                )
            )

        return parsed_value, next_cursor

    def __raise_eof_error(self) -> NoReturn:
        raise base.ParseError(
            f"Expected {self.__expected_type.__name__}, but found EOF"
        )

    def __raise_wrong_type_error(self, element: marko.element.Element) -> NoReturn:
        raise base.ParseError(
            f"Expected {self.__expected_type.__name__}, but found {type(element).__name__}"
        )

    def _validate_element(self, element: _T) -> None:
        """
        Override this method to implement specific element validation logic.

        :param element: The element to validate.
        """
        pass


class EOF[_V](base.IParser[_V, marko.element.Element]):
    def parse(
        self, state: base.State[_V, marko.element.Element]
    ) -> base.State[_V, marko.element.Element]:
        parsed_value, cursor = state
        current_element, next_cursor = cursor.next()

        if current_element is not None:
            raise base.ParseError(f"Expected EOF, but found {current_element}")

        return parsed_value, next_cursor


class RawText[_V](_ElementParser[_V, marko.inline.RawText]):
    def __init__(
        self,
        regex: re.Pattern[str],
        parse_element: Callable[[_V, marko.inline.RawText], _V] | None = None,
    ):
        super().__init__(
            expected_type=marko.inline.RawText,
            parse_element=parse_element,
        )
        self.__regex = regex

    @override
    def _validate_element(self, element: marko.inline.RawText) -> None:
        if self.__regex.fullmatch(element.children) is None:
            raise base.ParseError(
                f"Raw text does not match regex: {self.__regex.pattern}"
            )


class BlankLines[_V](base.IParser[_V, marko.element.Element]):
    def parse(
        self, state: base.State[_V, marko.element.Element]
    ) -> base.State[_V, marko.element.Element]:
        parsed_data, cursor = state

        while True:
            current_element, next_cursor = cursor.next()

            if current_element is None:
                break

            if not isinstance(current_element, marko.block.BlankLine):
                break

            cursor = next_cursor

        return parsed_data, cursor


# TODO: rewrite parse children element on client side
class Header[_V](_ElementParser[_V, marko.block.Heading]):
    def __init__(
        self,
        level: int,
        text_expr: re.Pattern[str],
        parse_element: Callable[[_V, marko.block.Heading], _V] | None = None,
    ):
        super().__init__(
            expected_type=marko.block.Heading,
            children_parser=base.Chain(RawText(text_expr), EOF()),
            parse_element=parse_element,
        )
        self.__level = level

    @override
    def _validate_element(self, element: marko.block.Heading) -> None:
        if element.level != self.__level:
            raise base.ParseError(
                f"Expected heading with level {self.__level} but found {element.level}"
            )


class List[_V](_ElementParser[_V, marko.block.List]):
    def __init__(
        self, list_item_parser: base.IParser[_V, marko.element.Element] | None = None
    ):
        super().__init__(
            expected_type=marko.block.List,
            children_parser=base.Repeat(
                parser=_ElementParser(
                    expected_type=marko.block.ListItem,
                    children_parser=list_item_parser,
                ),
                next_parser=EOF(),
            ),
        )


class Paragraph[_V](_ElementParser[_V, marko.block.Paragraph]):
    def __init__(
        self,
        children_parser: base.IParser[_V, marko.element.Element] | None = None,
        parse_element: Callable[[_V, marko.block.Paragraph], _V] | None = None,
    ):
        super().__init__(
            expected_type=marko.block.Paragraph,
            children_parser=children_parser,
            parse_element=parse_element,
        )


# TODO: rewrite parse children element on client side
class Link[_V](_ElementParser[_V, marko.inline.Link]):
    def __init__(
        self,
        text_expr: re.Pattern[str],
        parse_element: Callable[[_V, marko.inline.Link], _V] | None = None,
    ):
        super().__init__(
            expected_type=marko.inline.Link,
            children_parser=base.Chain(RawText(text_expr), EOF()),
            parse_element=parse_element,
        )
