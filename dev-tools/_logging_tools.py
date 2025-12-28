import logging
from typing import Mapping, Any, MutableMapping


class _PrefixLoggerAdapter(logging.LoggerAdapter):
    def __init__(
        self,
        logger: logging.Logger,
        extra: Mapping[str, object] | None = None,
        merge_extra: bool = False,
        *,
        prefix: str = "",
    ) -> None:
        super().__init__(logger, extra, merge_extra)
        self.__prefix = prefix

    def process(self, msg: Any, kwargs: MutableMapping[str, Any]) -> tuple[str, MutableMapping[str, Any]]:
        return f"[{self.__prefix}] {msg}", kwargs


def with_prefix(logger: logging.Logger, prefix: str) -> logging.Logger:
    return _PrefixLoggerAdapter(
        logger=logger,
        prefix=prefix,
    )
