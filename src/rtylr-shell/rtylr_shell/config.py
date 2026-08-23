"""Configuration and persistent-state handling for the appliance shell."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass
import json
import os
from pathlib import Path
import re
import tempfile
from typing import Any, Mapping


class ConfigError(ValueError):
    """Raised when shell configuration is invalid."""


DEFAULT_CONFIG: dict[str, Any] = {
    "brand": {
        "name": "Rtylr OS",
        "wordmark": "RTYLR",
        "accent": "#7c5cff",
    },
    "application": {
        "name": "Your business app",
        "command": ["/opt/rtylr/apps/business-app"],
        "working_directory": "/opt/rtylr/apps",
        "auto_start": True,
        "restart": {
            "max_attempts": 5,
            "window_seconds": 60,
            "backoff_seconds": [1, 2, 5, 10, 30],
        },
    },
    "ui": {"show_clock": True, "touch_control": True},
    "support": {"label": "Rtylr support", "url": "", "phone": ""},
}


@dataclass(frozen=True)
class Paths:
    default_config: Path
    runtime_config: Path
    state_file: Path
    application_log: Path
    device_id: Path

    @classmethod
    def runtime(cls) -> "Paths":
        return cls(
            default_config=Path("/opt/rtylr/config/shell.json"),
            runtime_config=Path("/var/lib/rtylr/shell.json"),
            state_file=Path("/var/lib/rtylr/shell-state.json"),
            application_log=Path("/var/log/rtylr/application.log"),
            device_id=Path("/var/lib/rtylr/device-id"),
        )


def deep_merge(base: Mapping[str, Any], override: Mapping[str, Any]) -> dict[str, Any]:
    """Merge nested mappings without mutating either input."""
    result = deepcopy(dict(base))
    for key, value in override.items():
        if isinstance(value, Mapping) and isinstance(result.get(key), Mapping):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = deepcopy(value)
    return result


def _read_json(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ConfigError(f"Could not read {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ConfigError(f"{path} must contain a JSON object")
    return value


def _normalize_legacy_config(config: Mapping[str, Any]) -> dict[str, Any]:
    """Map the 0.2 `pos` key to the neutral `application` model."""
    normalized = deepcopy(dict(config))
    legacy = normalized.pop("pos", None)
    current = normalized.get("application")
    if isinstance(legacy, Mapping):
        normalized["application"] = (
            deep_merge(legacy, current) if isinstance(current, Mapping) else deepcopy(dict(legacy))
        )
    return normalized


def _atomic_write_json(path: Path, value: Mapping[str, Any], mode: int = 0o640) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name = ""
    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=path.parent,
            prefix=f".{path.name}.",
            delete=False,
        ) as handle:
            json.dump(value, handle, indent=2, sort_keys=True)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
            temporary_name = handle.name
        os.chmod(temporary_name, mode)
        os.replace(temporary_name, path)
    finally:
        if temporary_name and os.path.exists(temporary_name):
            os.unlink(temporary_name)


def validate_config(config: Mapping[str, Any]) -> None:
    brand = config.get("brand")
    application = config.get("application")
    ui = config.get("ui")
    if (
        not isinstance(brand, Mapping)
        or not isinstance(application, Mapping)
        or not isinstance(ui, Mapping)
    ):
        raise ConfigError("brand, application, and ui must be objects")

    for key in ("name", "wordmark"):
        if not isinstance(brand.get(key), str) or not brand[key].strip():
            raise ConfigError(f"brand.{key} must be a non-empty string")
    if not isinstance(brand.get("accent"), str) or not re.fullmatch(
        r"#[0-9a-fA-F]{6}", brand["accent"]
    ):
        raise ConfigError("brand.accent must be a six-digit hex color")

    if not isinstance(application.get("name"), str) or not application["name"].strip():
        raise ConfigError("application.name must be a non-empty string")
    command = application.get("command")
    if not isinstance(command, list) or not command or not all(
        isinstance(part, str) and part for part in command
    ):
        raise ConfigError("application.command must be a non-empty string array")
    if not Path(command[0]).is_absolute():
        raise ConfigError("application.command executable must be an absolute path")
    working_directory = application.get("working_directory")
    if not isinstance(working_directory, str) or not Path(working_directory).is_absolute():
        raise ConfigError("application.working_directory must be an absolute path")
    if not isinstance(application.get("auto_start"), bool):
        raise ConfigError("application.auto_start must be true or false")

    restart = application.get("restart")
    if not isinstance(restart, Mapping):
        raise ConfigError("application.restart must be an object")
    maximum = restart.get("max_attempts")
    window = restart.get("window_seconds")
    backoff = restart.get("backoff_seconds")
    if not isinstance(maximum, int) or not 0 <= maximum <= 20:
        raise ConfigError("application.restart.max_attempts must be between 0 and 20")
    if not isinstance(window, int) or not 10 <= window <= 3600:
        raise ConfigError("application.restart.window_seconds must be between 10 and 3600")
    if not isinstance(backoff, list) or not backoff or not all(
        isinstance(delay, int) and 0 <= delay <= 300 for delay in backoff
    ):
        raise ConfigError("application.restart.backoff_seconds must contain delays from 0 to 300")

    if not isinstance(ui.get("show_clock"), bool) or not isinstance(ui.get("touch_control"), bool):
        raise ConfigError("ui flags must be true or false")


class ConfigStore:
    def __init__(self, paths: Paths):
        self.paths = paths

    def load(self) -> dict[str, Any]:
        defaults = _normalize_legacy_config(_read_json(self.paths.default_config))
        runtime = _normalize_legacy_config(_read_json(self.paths.runtime_config))
        config = deep_merge(DEFAULT_CONFIG, defaults)
        config = deep_merge(config, runtime)
        validate_config(config)
        return config

    def save(self, config: Mapping[str, Any]) -> None:
        normalized = _normalize_legacy_config(config)
        validate_config(normalized)
        _atomic_write_json(self.paths.runtime_config, normalized)


class StateStore:
    def __init__(self, paths: Paths):
        self.paths = paths
        self._state: dict[str, Any] = {}

    def load(self) -> dict[str, Any]:
        self._state = _read_json(self.paths.state_file)
        return deepcopy(self._state)

    def save(self, state: Mapping[str, Any] | None = None) -> None:
        if state is not None:
            self._state = deepcopy(dict(state))
        _atomic_write_json(self.paths.state_file, self._state, mode=0o600)

    def get(self, key: str, default: Any = None) -> Any:
        return self._state.get(key, default)

    def set(self, key: str, value: Any) -> None:
        self._state[key] = value

    @property
    def setup_complete(self) -> bool:
        return self._state.get("setup_complete") is True
