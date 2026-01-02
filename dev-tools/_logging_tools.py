import contextlib
import logging
from typing import Iterator, Mapping, Any, MutableMapping


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


@contextlib.contextmanager
def log_action(log: logging.Logger, action: str) -> Iterator[None]:
    log.debug(f"{action}: started")

    try:
        yield
    except Exception as e:
        log.debug(f"{action}: failed: {e}")
        raise
    else:
        log.debug(f"{action}: completed")
