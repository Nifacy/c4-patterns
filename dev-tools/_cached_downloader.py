import hashlib
from pathlib import Path
import logging
from typing import Final
import requests
import shutil


# TODO: add support of case when 2 urls have same cache key
class _CacheManager:
    def __init__(self, cache_path: Path) -> None:
        self.__cache_path = self.__validate_cache_path(cache_path)

    def get_cache_file(self, key: str) -> Path | None:
        cache_path = self.__cache_path / key
        return cache_path if cache_path.exists() else None

    def save_cache_file(self, key: str, src: Path) -> None:
        cache_path = self.__cache_path / key
        shutil.copy(src, cache_path)

    @staticmethod
    def __validate_cache_path(cache_path: Path) -> Path:
        if not cache_path.exists():
            cache_path.mkdir(parents=True)

        if not cache_path.is_dir():
            raise ValueError(f"'{cache_path}' is not directory")

        return cache_path


class CachedDownloader:
    _LOG_PREFIX: Final = "[CachedDownloader]"

    def __init__(self, log: logging.Logger, cache_path: Path) -> None:
        self.__log = log
        self.__cache_manager = _CacheManager(cache_path)

    def install_file(
        self,
        url: str,
        output_path: Path,
        *,
        percent_threshold: float = 10.0,
    ) -> None:
        self.__log.debug(f"{self._LOG_PREFIX} Install content from url '{url}' ...")

        cache_key = self.__get_cache_key(url)
        if (cache_path := self.__cache_manager.get_cache_file(cache_key)) is not None:
            self.__log.debug(f"{self._LOG_PREFIX} Use cached content")
            shutil.copy(cache_path, output_path)

        else:
            self.__log.debug(f"{self._LOG_PREFIX} Not found cached value. Install from server ...")

            with requests.get(url, stream=True) as response:
                with output_path.open("wb") as file:
                    total_installed_bytes = 0
                    last_logged_percent = 0.0
                    content_length = response.headers.get("Content-Length", None)
                    file_size = int(content_length) if content_length is not None else None

                    for chunk in response.iter_content(chunk_size=8_192):
                        if not isinstance(chunk, bytes) or not chunk:
                            continue

                        file.write(chunk)
                        total_installed_bytes += len(chunk)

                        if file_size is None:
                            continue

                        percent = total_installed_bytes / file_size * 100.0

                        if percent - last_logged_percent < percent_threshold:
                            continue

                        self.__log.debug(f"{self._LOG_PREFIX} Installed {percent:.2f}%")
                        last_logged_percent = percent

            self.__cache_manager.save_cache_file(cache_key, output_path)
            self.__log.debug(f"{self._LOG_PREFIX} Cache saved")

    @staticmethod
    def __get_cache_key(url: str) -> str:
        return hashlib.sha256(url.encode("utf-8")).hexdigest()
