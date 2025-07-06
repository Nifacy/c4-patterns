from __future__ import annotations

from typing import NoReturn, Sequence, override
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


class _ElementValidator[_T: Element]:
    def __init__(self, expected_type: type[_T], children_validator=None):
        self.__expected_type = expected_type
        self.__children_validator = children_validator

    def validate(self, cursor: Cursor) -> Cursor:
        current_element, next_cursor = cursor.next()

        if current_element is None:
            self.__raise_eof_error()

        if not isinstance(current_element, self.__expected_type):
            self.__raise_wrong_type_error()

        self._validate_element(current_element)
        if self.__children_validator is not None:
            self.__children_validator.validate(Cursor(current_element.children))

        return next_cursor

    def __raise_eof_error(self) -> NoReturn:
        raise ValidationError(
            f"Expected {self.__expected_type.__name__}, but found EOF"
        )

    def __raise_wrong_type_error(self, element: Element) -> NoReturn:
        raise ValidationError(
            f"Expected {self.__expected_type.__name__}, but found {type(element).__name__}"
        )

    def _validate_element(self, element: _T) -> None:
        """
        Override this method to implement specific element validation logic.

        :param element: The element to validate.
        """
        pass


class ValidateEOF:
    def validate(self, cursor: Cursor) -> Cursor:
        current_element, next_cursor = cursor.next()

        if current_element is not None:
            raise ValidationError(f"Expected EOF, but found {current_element}")

        return next_cursor


class ValidateRawText(_ElementValidator[RawText]):
    def __init__(self, regex: re.Pattern):
        super().__init__(RawText)
        self.__regex = regex

    @override
    def _validate_element(self, element: RawText) -> None:
        if self.__regex.fullmatch(element.children) is None:
            raise ValidationError(
                f"Raw text does not match regex: {self.__regex.pattern}"
            )


class ValidateHeader(_ElementValidator[Heading]):
    def __init__(self, level: int, text_expr: re.Pattern):
        super().__init__(
            expected_type=Heading,
            children_validator=Chain(ValidateRawText(text_expr), ValidateEOF()),
        )
        self.__level = level

    @override
    def _validate_element(self, element: Heading) -> None:
        if element.level != self.__level:
            raise ValidationError(
                f"Expected heading with level {self.__level} but found {element.level}"
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


class ValidateList(_ElementValidator[List]):
    def __init__(self, item_validator=None):
        super().__init__(
            expected_type=List,
            children_validator=_ElementValidator(
                expected_type=ListItem,
                children_validator=item_validator,
            ),
        )


class ValidateParagraph(_ElementValidator[Paragraph]):
    def __init__(self, item_validator=None):
        super().__init__(
            expected_type=Paragraph,
            children_validator=item_validator,
        )


class ValidateLink(_ElementValidator[Link]):
    def __init__(self, text_expr: re.Pattern):
        super().__init__(
            expected_type=Link,
            children_validator=Chain(ValidateRawText(text_expr), ValidateEOF()),
        )
