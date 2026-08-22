"""Narrowly scoped system and support actions exposed by the UI."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import socket
import subprocess
import time
from typing import Iterable


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    message: str


def _run(command: Iterable[str], timeout: float = 10.0) -> ActionResult:
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return ActionResult(False, str(exc))
    detail = completed.stderr.strip() or completed.stdout.strip()
    return ActionResult(completed.returncode == 0, detail)


def reconnect_network() -> ActionResult:
    disabled = _run(["nmcli", "networking", "off"])
    if not disabled.ok:
        return ActionResult(False, disabled.message or "Could not disable networking")
    time.sleep(0.5)
    enabled = _run(["nmcli", "networking", "on"])
    return ActionResult(enabled.ok, enabled.message or ("Network restarted" if enabled.ok else "Failed"))


def reboot() -> ActionResult:
    return _run(["loginctl", "reboot"])


def poweroff() -> ActionResult:
    return _run(["loginctl", "poweroff"])


def support_code(device_id_path: Path) -> str:
    try:
        source = device_id_path.read_text(encoding="utf-8").strip()
    except OSError:
        source = socket.gethostname()
    digest = hashlib.sha256(source.encode("utf-8")).hexdigest().upper()
    return f"{digest[:4]}-{digest[4:8]}"


def read_log_tail(path: Path, maximum_lines: int = 120) -> str:
    try:
        lines = path.read_text(encoding="utf-8", errors="replace").splitlines()
    except OSError:
        return "No POS log is available yet."
    return "\n".join(lines[-maximum_lines:]) or "The POS log is empty."
