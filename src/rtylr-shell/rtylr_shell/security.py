"""Admin PIN storage using a salted, deliberately expensive KDF."""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from typing import Any, Mapping


DEFAULT_ITERATIONS = 260_000


def valid_pin(pin: str) -> bool:
    return pin.isascii() and pin.isdigit() and 4 <= len(pin) <= 8


def hash_pin(
    pin: str,
    *,
    salt: bytes | None = None,
    iterations: int = DEFAULT_ITERATIONS,
) -> dict[str, Any]:
    if not valid_pin(pin):
        raise ValueError("PIN must contain four to eight digits")
    salt = salt or secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, iterations)
    return {
        "algorithm": "pbkdf2-sha256",
        "iterations": iterations,
        "salt": base64.b64encode(salt).decode("ascii"),
        "digest": base64.b64encode(digest).decode("ascii"),
    }


def verify_pin(pin: str, record: Mapping[str, Any] | None) -> bool:
    if (
        not isinstance(record, Mapping)
        or record.get("algorithm") != "pbkdf2-sha256"
        or not valid_pin(pin)
    ):
        return False
    try:
        iterations = int(record["iterations"])
        salt = base64.b64decode(record["salt"], validate=True)
        expected = base64.b64decode(record["digest"], validate=True)
        if not 1_000 <= iterations <= 2_000_000:
            return False
        if not 8 <= len(salt) <= 64 or len(expected) != 32:
            return False
        actual = hashlib.pbkdf2_hmac("sha256", pin.encode("utf-8"), salt, iterations)
    except (KeyError, OverflowError, TypeError, ValueError):
        return False
    return hmac.compare_digest(actual, expected)
