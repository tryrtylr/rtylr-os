"""Bounded business-application supervision without invoking a shell."""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass
import os
from pathlib import Path
import subprocess
import time
from typing import Any, Callable, Mapping


@dataclass(frozen=True)
class SupervisorSnapshot:
    status: str
    message: str
    pid: int | None
    last_exit_code: int | None
    next_restart_seconds: int | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


class AppSupervisor:
    def __init__(
        self,
        config: Mapping[str, Any],
        log_path: Path,
        *,
        clock: Callable[[], float] = time.monotonic,
        popen_factory: Callable[..., Any] = subprocess.Popen,
        executable_check: Callable[[str], bool] | None = None,
    ):
        self.config = dict(config)
        self.log_path = log_path
        self.clock = clock
        self.popen_factory = popen_factory
        self.executable_check = executable_check or (
            lambda path: Path(path).is_file() and os.access(path, os.X_OK)
        )
        self.process: Any | None = None
        self._log_handle: Any | None = None
        self._crashes: deque[float] = deque()
        self._restart_at: float | None = None
        self._manual_stop = False
        self.status = "idle"
        self.message = "Ready"
        self.last_exit_code: int | None = None

    def update_config(self, config: Mapping[str, Any]) -> None:
        self.config = dict(config)

    @property
    def running(self) -> bool:
        return self.process is not None and self.process.poll() is None

    def start(self, *, reset_failures: bool = False) -> bool:
        if self.running:
            return True
        if reset_failures:
            self._crashes.clear()
        self._manual_stop = False
        self._restart_at = None
        return self._launch()

    def _launch(self) -> bool:
        command = self.config.get("command", [])
        if not command or not self.executable_check(command[0]):
            self.status = "missing"
            self.message = (
                f"Business app executable not found: "
                f"{command[0] if command else 'not configured'}"
            )
            self.process = None
            return False
        working_directory = self.config.get("working_directory")
        if not working_directory or not Path(working_directory).is_dir():
            working_directory = str(Path(command[0]).parent)
        environment = os.environ.copy()
        environment["RTYLR_APPLIANCE"] = "1"
        try:
            self.log_path.parent.mkdir(parents=True, exist_ok=True)
            self._log_handle = self.log_path.open("a", encoding="utf-8", buffering=1)
            self.process = self.popen_factory(
                list(command),
                cwd=working_directory,
                env=environment,
                stdin=subprocess.DEVNULL,
                stdout=self._log_handle,
                stderr=subprocess.STDOUT,
                start_new_session=True,
            )
        except OSError as exc:
            self._close_log()
            self.process = None
            self.status = "failed"
            self.message = f"Could not start business app: {exc}"
            return False
        self.status = "running"
        self.message = f"{self.config.get('name', 'Business app')} is running"
        return True

    def poll(self) -> SupervisorSnapshot:
        now = self.clock()
        if self._restart_at is not None and now >= self._restart_at:
            self._restart_at = None
            self._launch()

        if self.process is not None:
            return_code = self.process.poll()
            if return_code is not None:
                self.last_exit_code = return_code
                self.process = None
                self._close_log()
                if self._manual_stop:
                    self.status = "stopped"
                    self.message = "Business app stopped"
                else:
                    self._handle_crash(now, return_code)
        return self.snapshot()

    def _handle_crash(self, now: float, return_code: int) -> None:
        restart = self.config.get("restart", {})
        window = int(restart.get("window_seconds", 60))
        maximum = int(restart.get("max_attempts", 5))
        while self._crashes and now - self._crashes[0] > window:
            self._crashes.popleft()
        self._crashes.append(now)
        if maximum == 0 or len(self._crashes) >= maximum:
            self.status = "failed"
            self.message = f"Business app stopped repeatedly (exit {return_code})"
            self._restart_at = None
            return
        backoff = restart.get("backoff_seconds", [1, 2, 5, 10, 30])
        delay = int(backoff[min(len(self._crashes) - 1, len(backoff) - 1)])
        self._restart_at = now + delay
        self.status = "restarting"
        self.message = f"Business app exited ({return_code}); restarting in {delay}s"

    def restart(self) -> bool:
        self.stop()
        self._manual_stop = False
        self._crashes.clear()
        return self.start(reset_failures=True)

    def stop(self) -> None:
        self._manual_stop = True
        self._restart_at = None
        if self.process is not None and self.process.poll() is None:
            try:
                self.process.terminate()
                self.process.wait(timeout=1.0)
            except subprocess.TimeoutExpired:
                try:
                    self.process.kill()
                    self.process.wait(timeout=1.0)
                except (OSError, subprocess.TimeoutExpired):
                    pass
            except OSError:
                pass
        self.process = None
        self._close_log()
        self.status = "stopped"
        self.message = "Business app stopped"

    def _close_log(self) -> None:
        if self._log_handle is not None:
            self._log_handle.close()
            self._log_handle = None

    def snapshot(self) -> SupervisorSnapshot:
        remaining: int | None = None
        if self._restart_at is not None:
            remaining = max(0, int(round(self._restart_at - self.clock())))
        pid = getattr(self.process, "pid", None) if self.running else None
        return SupervisorSnapshot(
            self.status,
            self.message,
            pid,
            self.last_exit_code,
            remaining,
        )


# Import compatibility for integrations written against Rtylr OS 0.2.
PosSupervisor = AppSupervisor
