import base64
import copy
from dataclasses import dataclass
import hashlib
import hmac
import io
import json
import re
import shutil
import subprocess
import sys
import time
from typing import Any, Final
import urllib.parse

import requests
import urllib
from ._interface import StructurizrWorkspaceExporter
from ._interface import ExportResult
from ._interface import ExportedWorkspace
from ._interface import ExportFailure
import os

from pathlib import Path


class _ConnectionTimeout(Exception):
    def __init__(self):
        super().__init__("Connection to the structurizr lite server timeout reached")



class _StructurizrLiteError(Exception):
    def __init__(self, source_error: Exception, stdout: str, stderr: str) -> None:
        self.source_error = source_error
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self) -> str:
        return f"Error has occurred from structurizr lite side.\nSource Error:\n{self.source_error}\nStdout:\n{self.stdout}\nStderr:\n{self.stderr}\n"


@dataclass
class _Credentials:
    api_key: str
    api_secret: str


@dataclass
class _AuthData:
    auth_token: str
    nonce: str


class StructurizrLite(StructurizrWorkspaceExporter):
    _STRUCTURIZR_LITE_FILENAME: Final = "structurizr-lite.war"
    _CONTEXT_FOLDER_NAME: Final = "context"
    _WORKSPACE_FOLDER_NAME: Final = "workspace"
    _JAVA_EXECUTABLE: Final = "java.exe" if sys.platform == "win32" else "java"

    _SERVER_ADDRESS: Final = "http://localhost:8080"
    _WORKSPACE_DEFAULT_FILE_NAME: Final = "workspace.dsl"

    _STRUCTURIZR_API_CLIENT_CALL_PATTERN: Final = re.compile(
        r"StructurizrApiClient\((.+)\)",
        flags=re.DOTALL,
    )

    def __init__(self, structurizr_lite_dir: Path, java_path: Path, syntax_plugin_path: Path, stdout_path: Path, stderr_path: Path):
        self.__structurizr_lite_dir = structurizr_lite_dir
        self.__java_path = java_path
        self.__syntax_plugin_path = syntax_plugin_path

        print(f"Stdout path: {stdout_path.absolute()}")
        print(f"Stderr path: {stderr_path.absolute()}")

        self.__structurizr_lite_jar = self.__get_structurizr_lite_jar_path(self.__structurizr_lite_dir)
        self.__context_dir = self.__get_context_directory(self.__structurizr_lite_dir)
        self.__workspace_dir = self.__get_workspace_directory(self.__context_dir)

        self.__server_process, self.__stdout, self.__stderr = self.__start_server(stdout_path, stderr_path)

    def export_to_json(self, workspace_path: Path) -> ExportResult:
        if self.__workspace_dir.exists():
            shutil.rmtree(self.__workspace_dir)

        shutil.copytree(workspace_path.parent, self.__workspace_dir, dirs_exist_ok=True)
        shutil.copyfile(workspace_path, self.__workspace_dir / self._WORKSPACE_DEFAULT_FILE_NAME)

        print("[StructurizrLite] Get workspace ...")

        print("[StructurizrLite] Get credentials ...")
        credentials = self.__get_credentials()
        print(f"[StructurizrLite] Credentials: {credentials}")

        try:
            print("[StructurizrLite] Get workspace ...")
            workspace = self.__get_workspace(credentials)
            print(f"[StructurizrLite] workspace: {json.dumps(workspace)}")
            return workspace
        except requests.HTTPError as e:
            if e.response.status_code == 400:
                return ExportFailure(e.response.content.decode("utf-8"))

            raise e

    def close(self) -> None:
        print("[StructurizrLite] Close ...")
        self.__server_process.kill()
        self.__server_process.wait()

        if self.__context_dir.exists():
            shutil.rmtree(self.__context_dir)

        self.__stdout.close()
        self.__stderr.close()

        print("[StructurizrLite] Close ... ok")

    @classmethod
    def __get_structurizr_lite_jar_path(cls, structurizr_lite_dir: Path) -> Path:
        structurizr_lite_jar = structurizr_lite_dir / cls._STRUCTURIZR_LITE_FILENAME
        if not structurizr_lite_jar.exists():
            raise FileNotFoundError(f"Structurizr Lite JAR not found at {structurizr_lite_jar}")
        return structurizr_lite_jar

    def __get_context_directory(self, structurizr_lite_dir: Path) -> Path:
        context_dir = structurizr_lite_dir / self._CONTEXT_FOLDER_NAME
        if context_dir.exists():
            shutil.rmtree(context_dir)
        return context_dir

    def __get_workspace_directory(self, context_dir: Path) -> Path:
        workspace_dir = context_dir / "workspace"
        workspace_dir.mkdir(parents=True)
        return workspace_dir

    def __start_server(self, stdout_path: Path, stderr_path: Path) -> tuple[subprocess.Popen, io.BufferedWriter, io.BufferedWriter]:
        print("Start Structurize Liter server ...")
        command = [
            str((self.__java_path / self._JAVA_EXECUTABLE).absolute()),
            f"-javaagent:{self.__syntax_plugin_path}",
            "-jar",
            str(self.__structurizr_lite_jar),
            str(self.__context_dir),
        ]

        env = os.environ.copy()
        env["STRUCTURIZR_WORKSPACE_PATH"] = self._WORKSPACE_FOLDER_NAME

        stdout = stdout_path.open('wb')
        stderr = stderr_path.open('wb')

        print(f"Command: {command}")
        process = subprocess.Popen(
            command,
            stdout=stdout,
            stderr=stderr,
            env=env,
        )

        try:
            self.__wait_for_connection()
        except _ConnectionTimeout as e:
            process.kill()
            process.wait()
            stdout.close()
            stderr.close()
            raise _StructurizrLiteError(
                source_error=e,
                stdout=stdout_path.read_text() if stdout_path.exists() else "",
                stderr=stderr_path.read_text() if stderr_path.exists() else "",
            )

        return process, stdout, stderr

    def __wait_for_connection(self, timeout: float = 60.0, delay: float = 5.0) -> None:
        start_time = time.time()

        while True:
            try:
                print("[Connection] Try health check server ...")
                request_timeout = (start_time + timeout) - time.time()
                if request_timeout <= 0.0:
                    raise _ConnectionTimeout()

                response = requests.get(
                    urllib.parse.urljoin(self._SERVER_ADDRESS, "/health"),
                    timeout=request_timeout,
                )
                response.raise_for_status()
                print("[Connection] Try health check server ... ok")
                return

            except (ConnectionError, OSError) as e:
                elapsed_time = time.time() - start_time
                print(f"[Connection] Health check failed. Elapsed time: {start_time}")

                if elapsed_time >= timeout:
                    raise _ConnectionTimeout() from e

                time.sleep(delay)

    def __get_credentials(self) -> _Credentials:
        response = requests.get("http://localhost:8080/workspace/diagrams")
        response.raise_for_status()

        page_html_content = response.content.decode()
        match = self._STRUCTURIZR_API_CLIENT_CALL_PATTERN.search(page_html_content)

        if match is None:
            raise RuntimeError("Unexpectedly, structurizr client's api call was not found")

        match_group = match.group(1)
        args = (line.strip().rstrip(',') for line in match_group.splitlines())
        args = tuple(line for line in args if line.strip())

        return _Credentials(
            api_key=args[2].strip('"'),
            api_secret=args[3].strip('"'),
        )

    def __get_workspace(self, credentials: _Credentials) -> ExportedWorkspace:
        auth_data = self.__get_auth_data(
            api_key=credentials.api_key,
            api_secret=credentials.api_secret,
            workspace_id=1,
        )

        response = requests.get(
            "http://localhost:8080/api/workspace/1",
            headers={
                "X-Authorization": auth_data.auth_token,
                "Nonce": auth_data.nonce,
            },
        )

        response.raise_for_status()
        return self.__normalize_workspace(response.json())


    def __get_auth_data(self, api_key: str, api_secret: str, workspace_id: int) -> _AuthData:
        nonce = str(int(time.time() * 1_000))
        content_md5 = hashlib.md5(b"").hexdigest()

        content_parts = ("GET", f"/api/workspace/{workspace_id}", content_md5, "", nonce)
        content = "".join(f"{el}\n" for el in content_parts)

        signature = hmac.new(
            key=api_secret.encode("utf-8"),
            msg=content.encode("utf-8"),
            digestmod=hashlib.sha256,
        ).hexdigest()

        signature_encoded = base64.b64encode(signature.encode()).decode("utf-8")
        auth_token = f"{api_key}:{signature_encoded}"

        return _AuthData(
            auth_token=auth_token,
            nonce=nonce,
        )

    def __normalize_workspace(self, workspace: dict[str, Any]) -> dict[str, Any]:
        normalized_workspace = copy.deepcopy(workspace)
        normalized_workspace.pop("lastModifiedDate", None)
        normalized_workspace["id"] = 0

        views = normalized_workspace.get("views", {})
        views_config = views.get("configuration", {})
        views_config.pop("lastSavedView", None)

        return normalized_workspace
