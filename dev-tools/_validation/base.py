from __future__ import annotations

from typing import Protocol


class ValidationError(Exception):
    pass


class Cursor[_T](Protocol):
    def next(self) -> tuple[_T | None, Cursor[_T]]:
        """
        Returns the current element and a new cursor which points on next element.
        If there are no more elements, returns None and the current cursor.
        """
        pass


class Validator[_T](Protocol):
    def validate(self, cursor: Cursor[_T]) -> Cursor[_T]:
        """
        Validates the current cursor.

        :raises ValidationError: if validation fails.
        :return: new cursor which points on next elements.
        """
        pass


class Chain[_T]:
    def __init__(self, *validators: Validator[_T]):
        self.__validators = validators

    def validate(self, cursor: Cursor[_T]) -> Cursor[_T]:
        for validator in self.__validators:
            cursor = validator.validate(cursor)
        return cursor


class Optional[_T](Validator[_T]):
    def __init__(self, validator: Validator[_T], then: Validator[_T] | None = None):
        self.__validator = validator
        self.__then = then

    def validate(self, cursor: Cursor[_T]) -> Cursor[_T]:
        try:
            cursor = self.__validator.validate(cursor)
        except ValidationError:
            return cursor

        return self.__then.validate(cursor) if self.__then is not None else cursor


class Repeat[_T](Validator[_T]):
    def __init__(self, validator: Validator[_T], next_validator: Validator[_T]):
        self.__validator = validator
        self.__next = next_validator

    def validate(self, cursor: Cursor[_T]) -> Cursor[_T]:
        while True:
            try:
                cursor = self.__validator.validate(cursor)
            except ValidationError:
                break

        return self.__next.validate(cursor)
