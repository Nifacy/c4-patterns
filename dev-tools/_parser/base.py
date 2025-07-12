from __future__ import annotations

from typing import Protocol


class ParseError(Exception):
    pass


class Cursor[_T](Protocol):
    def next(self) -> tuple[_T | None, Cursor[_T]]:
        """
        Returns the current element and a new cursor which points on next element.
        If there are no more elements, returns None and the current cursor.
        """
        ...


type State[_V, _T] = tuple[_V, Cursor[_T]]


class IParser[_V, _T](Protocol):
    def parse(self, state: State[_V, _T]) -> State[_V, _T]:
        """
        Validates the current cursor.

        :raises ValidationError: if validation fails.
        :return: new cursor which points on next elements.
        """
        ...


class _CursorWithMemory[_T](Cursor[_T]):
    def __init__(
        self, cursor: Cursor[_T], validated_items: tuple[_T, ...] | None = None
    ) -> None:
        self.__cursor = cursor
        self.__validated_items: tuple[_T, ...] = (
            validated_items if validated_items is not None else tuple()
        )

    def next(self) -> tuple[_T | None, Cursor[_T]]:
        item, next_cursor = self.__cursor.next()

        if item is None:
            return None, self

        return item, _CursorWithMemory(next_cursor, self.__validated_items + (item,))

    @property
    def validated_items(self) -> tuple[_T, ...]:
        return self.__validated_items

    @property
    def cursor(self) -> Cursor[_T]:
        return self.__cursor


class Chain[_V, _T](IParser[_V, _T]):
    def __init__(self, *parsers: IParser[_V, _T]):
        self.__parsers = parsers

    def parse(self, state: State[_V, _T]) -> State[_V, _T]:
        for parser in self.__parsers:
            state = parser.parse(state)
        return state


class Optional[_V, _T](IParser[_V, _T]):
    def __init__(self, condition: IParser[_V, _T], then: IParser[_V, _T] | None = None):
        self.__condition = condition
        self.__then = then

    def parse(self, state: State[_V, _T]) -> State[_V, _T]:
        try:
            state = self.__condition.parse(state)
        except ParseError:
            return state

        return self.__then.parse(state) if self.__then is not None else state


class Repeat[_V, _T](IParser[_V, _T]):
    def __init__(self, parser: IParser[_V, _T], next_parser: IParser[_V, _T]):
        self.__parser = parser
        self.__next = next_parser

    def parse(self, state: State[_V, _T]) -> State[_V, _T]:
        while True:
            try:
                state = self.__parser.parse(state)
            except ParseError:
                break

        return self.__next.parse(state)
