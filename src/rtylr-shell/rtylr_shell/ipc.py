"""Single-instance command channel used by Openbox shortcuts."""

from __future__ import annotations

import os
from pathlib import Path
import socket
import threading
from typing import Callable


ALLOWED_COMMANDS = {
    "show-recovery",
    "restart-app",
    "restart-pos",  # 0.2 compatibility alias
    "show-shell",
    "quit",
}


def socket_path() -> Path:
    runtime = os.environ.get("XDG_RUNTIME_DIR")
    if runtime:
        return Path(runtime) / "rtylr-shell.sock"
    return Path("/tmp") / f"rtylr-shell-{os.getuid()}.sock"


def send_command(command: str, path: Path | None = None) -> bool:
    if command not in ALLOWED_COMMANDS:
        raise ValueError(f"Unsupported command: {command}")
    target = path or socket_path()
    client = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
    client.settimeout(0.5)
    try:
        client.connect(str(target))
        client.sendall((command + "\n").encode("utf-8"))
        return True
    except OSError:
        return False
    finally:
        client.close()


class CommandServer:
    def __init__(self, callback: Callable[[str], None], path: Path | None = None):
        self.callback = callback
        self.path = path or socket_path()
        self._socket: socket.socket | None = None
        self._thread: threading.Thread | None = None
        self._stopping = threading.Event()

    def start(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
        server = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        server.bind(str(self.path))
        os.chmod(self.path, 0o600)
        server.listen(4)
        server.settimeout(0.5)
        self._socket = server
        self._thread = threading.Thread(target=self._serve, name="rtylr-ipc", daemon=True)
        self._thread.start()

    def _serve(self) -> None:
        assert self._socket is not None
        while not self._stopping.is_set():
            try:
                connection, _ = self._socket.accept()
            except socket.timeout:
                continue
            except OSError:
                break
            with connection:
                try:
                    command = connection.recv(128).decode("utf-8").strip()
                except (OSError, UnicodeDecodeError):
                    continue
                if command in ALLOWED_COMMANDS:
                    self.callback(command)

    def close(self) -> None:
        self._stopping.set()
        if self._socket is not None:
            self._socket.close()
        try:
            self.path.unlink()
        except FileNotFoundError:
            pass
