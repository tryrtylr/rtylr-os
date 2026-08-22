"""Fast, local-only health checks for common POS terminal failures."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path
import shutil
import subprocess
from typing import Callable, Iterable


@dataclass(frozen=True)
class CommandResult:
    returncode: int
    stdout: str = ""
    stderr: str = ""


@dataclass(frozen=True)
class HealthItem:
    key: str
    title: str
    status: str
    summary: str
    detail: str = ""

    def to_dict(self) -> dict[str, str]:
        return asdict(self)


Runner = Callable[[Iterable[str], float], CommandResult]


def run_command(command: Iterable[str], timeout: float = 2.0) -> CommandResult:
    try:
        completed = subprocess.run(
            list(command),
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return CommandResult(completed.returncode, completed.stdout.strip(), completed.stderr.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired) as exc:
        return CommandResult(127, "", str(exc))


def network_health(
    runner: Runner = run_command,
    interface_root: Path = Path("/sys/class/net"),
) -> HealthItem:
    result = runner(["nmcli", "-t", "-f", "STATE", "general"], 2.0)
    if result.returncode == 0:
        state = result.stdout.strip().lower()
        if state == "connected":
            return HealthItem("network", "Network", "ok", "Connected")
        if state in {"connecting", "connected (local only)", "connected (site only)"}:
            return HealthItem("network", "Network", "warning", state.capitalize())
        return HealthItem("network", "Network", "error", "Offline", state or "No connection")

    interfaces: list[str] = []
    if interface_root.exists():
        for interface in interface_root.iterdir():
            if interface.name == "lo":
                continue
            try:
                if (interface / "operstate").read_text(encoding="utf-8").strip() == "up":
                    interfaces.append(interface.name)
            except OSError:
                continue
    if interfaces:
        return HealthItem(
            "network", "Network", "warning", "Link available", ", ".join(sorted(interfaces))
        )
    return HealthItem("network", "Network", "error", "Offline", "No active interface")


def storage_health(path: Path = Path("/")) -> HealthItem:
    try:
        total, _used, free = shutil.disk_usage(path)
    except OSError as exc:
        return HealthItem("storage", "Storage", "error", "Unavailable", str(exc))
    free_ratio = free / total if total else 0
    free_gib = free / (1024**3)
    summary = f"{free_gib:.1f} GB free"
    if free_gib < 2 or free_ratio < 0.05:
        status = "error"
    elif free_ratio < 0.15:
        status = "warning"
    else:
        status = "ok"
    return HealthItem("storage", "Storage", status, summary)


def printing_health(runner: Runner = run_command) -> HealthItem:
    daemon = runner(["lpstat", "-r"], 2.0)
    if daemon.returncode == 127:
        return HealthItem("printing", "Printing", "warning", "Tools unavailable")
    if daemon.returncode != 0:
        return HealthItem("printing", "Printing", "error", "Service unavailable", daemon.stderr)
    printers = runner(["lpstat", "-p"], 2.0)
    printer_lines = [line for line in printers.stdout.splitlines() if line.startswith("printer ")]
    count = len(printer_lines)
    if count:
        ready = sum(1 for line in printer_lines if " disabled " not in f" {line.lower()} ")
        if ready != count:
            paused = count - ready
            return HealthItem(
                "printing",
                "Printing",
                "warning",
                f"{ready} ready, {paused} paused",
            )
        label = "printer" if count == 1 else "printers"
        return HealthItem("printing", "Printing", "ok", f"{count} {label} ready")
    return HealthItem("printing", "Printing", "warning", "No printer configured")


def usb_health(usb_root: Path = Path("/sys/bus/usb/devices")) -> HealthItem:
    try:
        count = 0
        for item in usb_root.iterdir():
            if not (item / "idVendor").exists():
                continue
            try:
                device_class = (item / "bDeviceClass").read_text(encoding="utf-8").strip()
            except OSError:
                device_class = ""
            if device_class != "09":
                count += 1
    except OSError:
        return HealthItem("usb", "USB devices", "warning", "Could not inspect")
    if count:
        return HealthItem("usb", "USB devices", "ok", f"{count} detected")
    return HealthItem("usb", "USB devices", "warning", "No peripherals detected")


def collect_health() -> list[HealthItem]:
    return [network_health(), storage_health(), printing_health(), usb_health()]
