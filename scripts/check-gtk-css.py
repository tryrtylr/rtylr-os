"""Validate the shell stylesheet with GTK's own CSS parser when available."""

from __future__ import annotations

import ctypes
from ctypes.util import find_library
from pathlib import Path
import sys


class GError(ctypes.Structure):
    _fields_ = [
        ("domain", ctypes.c_uint),
        ("code", ctypes.c_int),
        ("message", ctypes.c_char_p),
    ]


def main() -> int:
    gtk_name = find_library("gtk-3")
    glib_name = find_library("glib-2.0")
    gobject_name = find_library("gobject-2.0")
    if not all((gtk_name, glib_name, gobject_name)):
        print("GTK 3 unavailable; skipping native CSS parse.", file=sys.stderr)
        return 0

    gtk = ctypes.CDLL(gtk_name)
    glib = ctypes.CDLL(glib_name)
    gobject = ctypes.CDLL(gobject_name)
    gtk.gtk_css_provider_new.restype = ctypes.c_void_p
    gtk.gtk_css_provider_load_from_path.argtypes = [
        ctypes.c_void_p,
        ctypes.c_char_p,
        ctypes.POINTER(ctypes.POINTER(GError)),
    ]
    gtk.gtk_css_provider_load_from_path.restype = ctypes.c_int
    glib.g_error_free.argtypes = [ctypes.POINTER(GError)]
    gobject.g_object_unref.argtypes = [ctypes.c_void_p]

    provider = gtk.gtk_css_provider_new()
    error = ctypes.POINTER(GError)()
    css_path = Path(sys.argv[1]).resolve()
    loaded = gtk.gtk_css_provider_load_from_path(
        provider, str(css_path).encode(), ctypes.byref(error)
    )
    try:
        if error:
            print(f"GTK CSS error: {error.contents.message.decode()}", file=sys.stderr)
            return 1
        if not loaded:
            print("GTK CSS parser returned failure.", file=sys.stderr)
            return 1
        print("GTK 3 CSS parser: OK")
        return 0
    finally:
        if error:
            glib.g_error_free(error)
        gobject.g_object_unref(provider)


if __name__ == "__main__":
    raise SystemExit(main())
