from __future__ import annotations

from typing import NoReturn, Sequence, override
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
        return self.__elements[self.__index], MarkdownCursor(self.__elements, self.__index + 1)


class _ElementValidator[_T: marko.element.Element](
    base.Validator[marko.element.Element]
):
    def __init__(
        self,
        expected_type: type[_T],
        children_validator: base.Validator[marko.element.Element] | None = None,
    ):
        self.__expected_type = expected_type
        self.__children_validator = children_validator

    def validate(self, cursor: MarkdownCursor) -> MarkdownCursor:
        current_element, next_cursor = cursor.next()

        if current_element is None:
            self.__raise_eof_error()

        if not isinstance(current_element, self.__expected_type):
            self.__raise_wrong_type_error()

        self._validate_element(current_element)
        if self.__children_validator is not None:
            self.__children_validator.validate(MarkdownCursor(current_element.children))

        return next_cursor

    def __raise_eof_error(self) -> NoReturn:
        raise base.ValidationError(
            f"Expected {self.__expected_type.__name__}, but found EOF"
        )

    def __raise_wrong_type_error(self, element: marko.element.Element) -> NoReturn:
        raise base.ValidationError(
            f"Expected {self.__expected_type.__name__}, but found {type(element).__name__}"
        )

    def _validate_element(self, element: _T) -> None:
        """
        Override this method to implement specific element validation logic.

        :param element: The element to validate.
        """
        pass


class ValidateEOF(base.Validator[marko.element.Element]):
    def validate(self, cursor: MarkdownCursor) -> MarkdownCursor:
        current_element, next_cursor = cursor.next()

        if current_element is not None:
            raise base.ValidationError(f"Expected EOF, but found {current_element}")

        return next_cursor


class ValidateRawText(_ElementValidator[marko.inline.RawText]):
    def __init__(self, regex: re.Pattern):
        super().__init__(marko.inline.RawText)
        self.__regex = regex

    @override
    def _validate_element(self, element: marko.inline.RawText) -> None:
        if self.__regex.fullmatch(element.children) is None:
            raise base.ValidationError(
                f"Raw text does not match regex: {self.__regex.pattern}"
            )


class SkipBlankLines:
    def validate(self, cursor: MarkdownCursor) -> MarkdownCursor:
        while True:
            current_element, next_cursor = cursor.next()

            if current_element is None:
                return next_cursor

            if not isinstance(current_element, marko.block.BlankLine):
                return cursor

            cursor = next_cursor


class ValidateHeader(_ElementValidator[marko.block.Heading]):
    def __init__(self, level: int, text_expr: re.Pattern):
        super().__init__(
            expected_type=marko.block.Heading,
            children_validator=base.Chain(ValidateRawText(text_expr), ValidateEOF()),
        )
        self.__level = level

    @override
    def _validate_element(self, element: marko.block.Heading) -> None:
        if element.level != self.__level:
            raise base.ValidationError(
                f"Expected heading with level {self.__level} but found {element.level}"
            )


class ValidateList(_ElementValidator[marko.block.List]):
    def __init__(
        self, children_validator: base.Validator[marko.element.Element] | None = None
    ):
        super().__init__(
            expected_type=marko.block.List,
            children_validator=_ElementValidator(
                expected_type=marko.block.ListItem,
                children_validator=children_validator,
            ),
        )


class ValidateParagraph(_ElementValidator[marko.block.Paragraph]):
    def __init__(
        self, children_validator: base.Validator[marko.element.Element] | None = None
    ):
        super().__init__(
            expected_type=marko.block.Paragraph,
            children_validator=children_validator,
        )


class ValidateLink(_ElementValidator[marko.inline.Link]):
    def __init__(self, text_expr: re.Pattern):
        super().__init__(
            expected_type=marko.inline.Link,
            children_validator=base.Chain(ValidateRawText(text_expr), ValidateEOF()),
        )
