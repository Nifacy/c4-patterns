from __future__ import annotations

from typing import NoReturn, Sequence
from marko.element import Element
from marko.block import Heading, BlankLine, List, Paragraph, ListItem
from marko.inline import RawText, Link
import re


class ValidationError(Exception):
    pass


class Cursor:
    def __init__(self, elements: Sequence[Element], index: int = 0):
        self.__elements = elements
        self.__index = index

    def next(self) -> tuple[Element | None, Cursor]:
        if self.__index >= len(self.__elements):
            return None, self

        return self.__elements[self.__index], Cursor(self.__elements, self.__index + 1)


class ValidateHeader:
    def __init__(self, level: int, text_expr: re.Pattern):
        self.__level = level
        self.__text_expr = text_expr

    def validate(self, cursor: Cursor) -> Cursor:
        current_element, next_cursor = cursor.next()

        if current_element is None:
            self.__raise_error(current_element)

        if not isinstance(current_element, Heading):
            self.__raise_error(current_element)

        if current_element.level != self.__level:
            self.__raise_error(current_element)

        self.__validate_header_content(current_element)

        return next_cursor

    def __validate_header_content(self, element: Heading) -> None:
        if not isinstance(element.children[0], RawText):
            self.__raise_error(element)

        content = element.children[0].children

        if self.__text_expr.fullmatch(content) is None:
            self.__raise_error(element)

    def __raise_error(self, element: Element | None) -> NoReturn:
        repr_element = repr(element) if element is not None else "EOF"
        raise ValidationError(
            f"Expected heading with (level={self.__level}, text={self.__text_expr}), but found {repr_element}"
        )


class SkipBlankLines:
    def validate(self, cursor: Cursor) -> Cursor:
        while True:
            current_element, next_cursor = cursor.next()

            if current_element is None:
                return next_cursor

            if not isinstance(current_element, BlankLine):
                return cursor

            cursor = next_cursor


class ValidateList:
    def __init__(self, item_validator=None):
        self.__item_validator = item_validator

    def validate(self, cursor: Cursor) -> Cursor:
        current_element, next_cursor = cursor.next()

        if current_element is None:
            self.__raise_error(current_element)

        if not isinstance(current_element, List):
            self.__raise_error(current_element)

        if self.__item_validator is not None:
            for item in current_element.children:
                if not isinstance(item, ListItem):
                    self.__raise_item_error(item)
                self.__item_validator.validate(Cursor(item.children))

        return next_cursor

    def __raise_error(self, element: Element | None) -> NoReturn:
        repr_element = repr(element) if element is not None else "EOF"
        raise ValidationError(f"Expected list, but found {repr_element}")

    def __raise_item_error(self, element: Element) -> NoReturn:
        raise ValidationError(f"Expected list item, but found {element}")


class Chain:
    def __init__(self, *validators):
        self.__validators = validators

    def validate(self, cursor: Cursor) -> Cursor:
        for validator in self.__validators:
            cursor = validator.validate(cursor)
        return cursor


class Optional:
    def __init__(self, validator, then=None):
        self.__validator = validator
        self.__then = then

    def validate(self, cursor: Cursor) -> Cursor:
        try:
            cursor = self.__validator.validate(cursor)
        except ValidationError:
            return cursor

        return self.__then.validate(cursor) if self.__then is not None else cursor


class ValidateParagraph:
    def __init__(self, item_validator=None):
        self.__item_validator = item_validator

    def validate(self, cursor: Cursor) -> Cursor:
        current_element, next_cursor = cursor.next()

        if current_element is None:
            return next_cursor

        if not isinstance(current_element, Paragraph):
            raise ValidationError(f"Expected paragraph, but found {current_element}")

        if self.__item_validator is not None:
            self.__item_validator.validate(Cursor(current_element.children))

        return next_cursor


class ValidateRawText:
    def __init__(self, regex: re.Pattern):
        self.__regex = regex

    def validate(self, cursor: Cursor) -> Cursor:
        current_element, next_cursor = cursor.next()

        if current_element is None:
            return next_cursor

        if not isinstance(current_element, RawText):
            raise ValidationError(f"Expected raw text, but found {current_element}")

        if self.__regex.fullmatch(current_element.children) is None:
            raise ValidationError(
                f"Raw text does not match regex: {self.__regex.pattern}"
            )

        return next_cursor


class ValidateLink:
    def __init__(self, text_expr: re.Pattern):
        self.__text_expr = text_expr

    def validate(self, cursor: Cursor) -> Cursor:
        current_element, next_cursor = cursor.next()

        if current_element is None:
            return next_cursor

        if not isinstance(current_element, Link):
            raise ValidationError(f"Expected link, but found {current_element}")

        if not isinstance(current_element.children[0], RawText):
            raise ValidationError(
                f"Expected raw text in link, but found {current_element.children[0]}"
            )

        content = current_element.children[0].children

        if self.__text_expr.fullmatch(content) is None:
            raise ValidationError(
                f"Link text does not match regex: {self.__text_expr.pattern}"
            )

        return next_cursor


class Repeat:
    def __init__(self, validator, next_validator):
        self.__validator = validator
        self.__next = next_validator

    def validate(self, cursor: Cursor) -> Cursor:
        while True:
            try:
                cursor = self.__validator.validate(cursor)
            except ValidationError:
                break

        return self.__next.validate(cursor)


class ValidateEOF:
    def validate(self, cursor: Cursor) -> Cursor:
        current_element, next_cursor = cursor.next()

        if current_element is not None:
            raise ValidationError(f"Expected EOF, but found {current_element}")

        return next_cursor
